var gulp = require('gulp');
var sass = require('gulp-sass');
var sourcemaps = require('gulp-sourcemaps');
var notify = require("gulp-notify");
var rename = require("gulp-rename");
var browserify = require('browserify');
var babelify = require('babelify');
var source = require('vinyl-source-stream');
var gutil = require('gulp-util');
var buffer = require('vinyl-buffer');


gulp.task('sass', function() {
    return gulp.src('static/**/*.scss')
        .pipe(sourcemaps.init())
        .pipe(sass({
            follow: true
        }))
        .pipe(sourcemaps.write('./maps'))
        .pipe(rename(function(path){
            path.extname = ".min" + path.extname;
            return path;
        }))
        .pipe(gulp.dest('dist'))
        .pipe(notify("Built SASS!"));
});


gulp.task('scripts', function() {
    var b = browserify({
            "entries": ['static/js/app.js'],
            transform: [babelify]
        });
    
    return b.bundle()
        .pipe(source('app.min.js'))
        .pipe(buffer())
        .pipe(sourcemaps.init({loadMaps: true}))
            .on('error', gutil.log)
        .pipe(sourcemaps.write('./maps'))
        .pipe(gulp.dest('dist/js'))
        .pipe(notify("Built JS!"));
});


gulp.task('watch', function() {
    gulp.watch('**/*.scss', ['sass']);
    gulp.watch('**/*.js', ['scripts']);
});


gulp.task("default", ["sass", "scripts"]);