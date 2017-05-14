const gulp = require('gulp');
const notify = require("gulp-notify");
const plumber = require('gulp-plumber');

// All
const sourcemaps = require('gulp-sourcemaps');
const rename = require("gulp-rename");

// CSS
const sass = require('gulp-sass');
const autoprefixer = require('gulp-autoprefixer');

// JS Processing
const rollup = require('rollup').rollup;
const babel_rollup = require('rollup-plugin-babel');
const nodeResolve = require('rollup-plugin-node-resolve');
const uglify_rollup = require('rollup-plugin-uglify');


var onError = function(err) {
  notify.onError({
    title: "Gulp",
    subtitle: "Failure!",
    message: "Error: <%= error.message %>",
    sound: "Beep"
  })(err);

  this.emit('end');
};


gulp.task('css', function() {
  return gulp.src('frontend/**/*.scss')
    .pipe(plumber({
      errorHandler: onError
    }))
    .pipe(sourcemaps.init())
    .pipe(sass({
      follow: true
    }))
    .pipe(autoprefixer())
    .pipe(sourcemaps.write('./maps'))
    .pipe(rename(function(path) {
      path.extname = ".min" + path.extname;
      return path;
    }))
    .pipe(gulp.dest('dist'))
    .pipe(notify("Built SASS!"));
});


//
// Build js files
// @param {string} name - Module name
// @param {string} outdir - The subdirectory to write into
// @param {boolean} minify - Should the file be uglified
// @param {string} format - Output format. UMD or IIFE
//
let buildJS = function(name, inpath, outpath, format, minify) {

  format = (format === undefined) ? "iife" : format;

  let plugins = [
    nodeResolve({
      jsnext: true,
      browser: true,
    }),
    babel_rollup(),
  ]
  if (minify) {
    plugins.push(uglify_rollup({
      mangle: true,
    }));
  }

  return rollup({
    entry: inpath,
    plugins: plugins,
  }).then(function(bundle) {
    return bundle.write({
      treeshake: false,
      format: format,
      dest: outpath,
      sourceMap: true,
    });
  });
};


//
// Create js for distribution
//
gulp.task("js", () => {

  let tasks = [];

  // Compat
  tasks.push(buildJS("app", "frontend/js/app.js", "dist/js/app.js", "iife"));
  tasks.push(buildJS("app", "frontend/js/app.js", "dist/js/app.min.js", "iife", true));
});


gulp.task('watch', function() {
  gulp.watch('frontend/**/*.scss', ['css']);
  gulp.watch('frontend/**/*.js', ['js']);
});

gulp.task("default", ["css", "js"]);