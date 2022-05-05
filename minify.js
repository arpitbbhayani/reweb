const purgeCSS = require("purgecss");
const CleanCSS = require('clean-css');
const fs = require("fs");
const purgeCSSResults = new purgeCSS.PurgeCSS().purge({
  content: ["dist/**/*.html"],
  css: ["dist/**/*.css"],
});
purgeCSSResults.then((x) => {
  const options = {}
  const output = new CleanCSS(options).minify(x[0].css);
  fs.writeFileSync("dist/static/style.min.css", output.styles);
})
