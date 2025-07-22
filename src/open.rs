use crate::shell::Shell;
use anyhow::{bail, Context as _};
use camino::Utf8Path;
use serde_json::json;
use std::{borrow::Borrow, path::Path};
use url::Url;

pub(crate) fn open(
    urls: &[impl Borrow<Url>],
    open: Option<impl AsRef<str>>,
    paths: &[(impl AsRef<Utf8Path>, impl AsRef<Utf8Path>)],
    pkg_manifest_dir: &Utf8Path,
    process_cwd: &Utf8Path,
    shell: &mut Shell,
) -> anyhow::Result<()> {
    for url in urls {
        let url = url.borrow();
        shell.status("Opening", url)?;
        opener::open(url.as_str())?;
    }

    if let Some(open) = open {
        fn ensure_utf8(path: &Path) -> anyhow::Result<&str> {
            path.to_str()
                .with_context(|| format!("must be UTF-8: {:?}", path.display()))
        }

        let input = json!({
            "git_workdir": gix::discover(process_cwd)
                .ok()
                .and_then(|r| {
                    r.worktree()
                        .map(|wt| ensure_utf8(wt.base()).map(ToOwned::to_owned))
                })
                .transpose()?,
            "manifest_dir": pkg_manifest_dir,
            "paths": paths
                .iter()
                .map(|(src_path, test_suite_path)| {
                    json!({
                        "src": src_path.as_ref(),
                        "test_suite": test_suite_path.as_ref()
                    })
                })
                .collect::<Vec<_>>()
        })
        .to_string();

        let jq = crate::process::which("jq", process_cwd).with_context(|| {
            "`jq` not found. install `jq` from https://github.com/stedolan/jq/releases"
        })?;

        let output = crate::process::process(jq)
            .args(&["-c", open.as_ref()])
            .pipe_input(Some(input))
            .cwd(process_cwd)
            .read_with_shell_status(shell)?;

        let commands = if let Ok(commands) = serde_json::from_str::<Vec<Vec<String>>>(&output) {
            commands
        } else if let Ok(command) = serde_json::from_str(&output) {
            vec![command]
        } else {
            bail!("expected `string[] | string[][]`");
        };

        for command in commands {
            if let [program, args @ ..] = &*command {
                crate::process::with_which(program, process_cwd)?
                    .args(args)
                    .exec_with_shell_status(shell)?;
            }
        }
    }
    Ok(())
}
