# Parole branch routing

- Start UI, interaction, styles and front-end assets on `front-end`. Keep that work on that branch and record visible changes in `web/CHANGELOG.md`.
- Start curriculum, SQLite, schema and course export changes on `main`. Split mixed requests by branch. Merge updates from main into front-end when frontend code needs the new schema or export contract.
- GitHub Pages assembles the UI from front-end and course data built from main. Do not merge UI changes into main just to publish.
- When using a local Git checkout, enable the versioned guard with `git config core.hooksPath .githooks`.

Front-end pushes run **Check front-end**. Successful checks trigger the Pages workflow from main, since the Pages environment deploys only from the default branch.
