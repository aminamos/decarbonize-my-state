# Decarb My State

> [!IMPORTANT]
> Decarb My State isn't currently in active development - the climate change group at [Chi Hack Night](https://chihacknight.org/) is now working on other projects - see our [breakout group issue](https://github.com/chihacknight/breakout-groups/issues/215) to see what we're up to right now!

Chi Hack Night data visualization project to measure the state and progress of decarbonization for all States in the USA.

- [Running project notes](https://docs.google.com/document/d/14gs7gO9YmBgIWOMd7oGXmIF1XRwfBIt8jGTOpn8udjg/edit#heading=h.n9cfl96c3r81)
- [Wireframes](https://app.moqups.com/pcSQvUMmsyAa1SN58KaKg1EKuYRs8iRX/view/page/a68639957)

This is an [Astro](https://astro.build/) app. It was originally built as a Gatsby site on top of the [DataMade Gatsby starter template](https://github.com/datamade/how-to/tree/master/docker/templates), and was migrated to Astro (React islands via `@astrojs/react`). Static HTML is generated at build time for every route and deployed as a Cloudflare Worker serving the `dist/` directory.

### 💾 Requirements

- [Docker](https://docs.docker.com/install/)
- [Docker Compose](https://docs.docker.com/compose/install/)
- Node 20+ (developed on Node 22/26)

### 🚀 Quick start

1. Grab the repo:

   ```shell
   git clone git@github.com:chihacknight/decarbonize-my-state.git
   cd decarbonize-my-state
   ```

2. Start developing

   ```shell
   yarn install
   ```
   to install dependencies, then
   ```shell
   yarn dev
   ```

   (or `docker-compose up --build`, which runs `yarn dev` in a container)

   Your site should now be up and running at `http://localhost:8000`!

## Dependencies

This starter has a minimal number of dependencies in order to stay lean, but you'll likely want to add more to suit your needs. To add a dependency, run:

```shell
docker-compose run --rm app add <dependency name> --save
```

or

```shell
yarn add <dependency name>
```

To remove a dependency:

```shell
docker-compose run --rm app remove <dependency name>
```

or

```shell
yarn remove <dependency name>
```

## Testing & syntax linting

Formatting is enforced with [Prettier](https://prettier.io/). To check it:

```shell
yarn test
```

To reformat:

```shell
yarn format
```

## Build

To produce the static site in `dist/`:

```shell
yarn build
```

## Data processing

All data that appears on the frontend of this site should come directly from a file in `data/final`—for more on that line of thinking, see [this guide to data handling](https://github.com/datamade/how-to/blob/master/gatsby/recharts.md#on-data-transformation) in Gatsby. The data processing pipeline for this project lives in `data/` and follows DataMade's [data making guidelines](https://github.com/datamade/data-making-guidelines). As these files are relatively small, we keep both raw and final data under version control.

To recreate the data, run:

```bash
cd data
docker-compose up --build
```

### Social Cards

We wanted the social cards to include what number emitter the state is and what their emissions breakdown is. To do this, we created a social card page and used puppeteer to take screenshots to output get the dynamic social cards. The new screenshots can be found in `/static/social-cards`

**To generate them:**

First make sure `yarn dev` is running (the dev server is pinned to port 8000)

Then run `yarn generate-social-all` to generate all social images (~3,500), or run:
- `yarn generate-social-states` for just state social images (50)
- `yarn generate-social-power-plants` for just powerplants (~3,500)

To then show progress logs, just tack on `--debugging`, e.g. `yarn generate social-power-plants --debugging`.

**Finally:** Copy `/power-plant-social-out/social-cards/power-plants` into
`static/social-cards/power-plants`. We write power plant cards to a scratch directory first because
writing that many files into `static/` triggers a dev-server reload for every file.

### 🤖 What's inside?

A quick look at the top-level files and directories in this Astro project.

    .
    ├── .github/workflows     # CI (Prettier check)
    ├── data/                 # raw + final data (data/final/** is what the site reads)
    ├── scripts/              # social card generator (puppeteer)
    ├── src/
    │   ├── pages/            # Astro routes (file-based)
    │   ├── layouts/          # Base.astro — document head + global CSS
    │   ├── views/            # React page components rendered as islands
    │   ├── components/       # React components (charts, map, layout chrome)
    │   ├── constants/        # citations, terminology, state names
    │   ├── lib/data.js       # build-time data accessors over data/final/**
    │   ├── images/           # bundled images
    │   └── styles/           # global + per-page CSS
    ├── static/               # served verbatim at the site root (social cards, plant images)
    ├── astro.config.mjs
    ├── package.json
    └── wrangler.jsonc

1.  **`/src/pages`**: File-based routes. `index.astro`, `about.astro`, etc. are static pages;
    `[state]/index.astro` and `[state]/power-plant/[slug].astro` generate one page per state and
    per power plant via `getStaticPaths`.

2.  **`/src/lib/data.js`**: Astro has no GraphQL data layer, so this module reads `data/final/**`
    directly and returns it in the `{ allXJson: { edges: [{ node }] } }` shape the React components
    expect. Filtering happens at build time so only the page's slice reaches the client.

3.  **`/src/views`**: The React page bodies, rendered with `client:load` so they server-render (for
    SEO) and then hydrate (for charts, the map, and tooltips).

4.  **`/static`**: Copied verbatim into `dist/` (configured via `publicDir` in `astro.config.mjs`).
    Do not import from here; reference these paths directly.

5.  **`wrangler.jsonc`**: Cloudflare Workers static assets config; serves `./dist`.

### 🎓 Learning Astro

- [Astro documentation](https://docs.astro.build/)
- [React integration](https://docs.astro.build/en/guides/integrations-guide/react/)

### 💫 Deploy

The site is deployed to Cloudflare as a Workers static-assets Worker:

```shell
yarn build
wrangler deploy
```

`wrangler.jsonc` points the Worker at `./dist` and serves `404.html` for unmatched routes.
