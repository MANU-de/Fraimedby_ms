# Framedby static reference project

A static site based on the supplied Framedby HTML. Python 3.12+ generates HTML using only its standard library. The browser uses HTML, CSS and JavaScript.

```sh
python build.py
python -m unittest discover -s tests
python -m http.server 8000 --directory dist
```

Open http://localhost:8000. The generated `dist` directory is also included for preview or direct upload. Serve it over HTTP so directory links resolve consistently.

- Edit `src/home.html` for the reference homepage shell, `src/detail.html` for the reusable lab reader and `src/assets` for interaction and styling.
- Edit `content/labs.json` once to update a catalog entry and its lab page. A planned entry has no bundle or run link. The bundled lab is verified with local Python. Its Compose files are included for optional container use.
- Set `repository` to your GitHub owner/name in `content/site.json` to enable the prefilled reproduction issue link. After CI passes, put the exact workflow run URL in the lab's `verificationRun` field.
- The **Support Framedby** page is a placeholder. Set `donationUrl` to an HTTPS donation page when you have one.
- The homepage retains the reference design's Tailwind, icon, and font CDN dependencies. The lab reader uses local styles.

Connect the repository to Netlify using the included build settings, or deploy the generated `dist` directory to GitHub Pages using your Pages publishing workflow. Add `framedby.ms` through the hosting provider's domain settings and apply the DNS records it provides. Relative links also work on GitHub Pages project URLs.

Source code uses Apache-2.0. The original HTML was supplied as the design reference. The included lab bundle carries its own license file.
