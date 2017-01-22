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
var browserSync = require('browser-sync');
var reload = browserSync.reload;
var plumber = require('gulp-plumber');
var spawn = require('child_process').spawn;


var onError = function(err) {
    notify.onError({
        title:    "Gulp",
        subtitle: "Failure!",
        message:  "Error: <%= error.message %>",
        sound:    "Beep"
    })(err);

    this.emit('end');
};


gulp.task('sass', function() {
    return gulp.src('static/**/*.scss')
        .pipe(plumber({errorHandler: onError}))
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
        .on('error', onError)
        .pipe(source('app.min.js'))
        .pipe(buffer())
        .pipe(sourcemaps.init({loadMaps: true}))
            .on('error', gutil.log)
        .pipe(sourcemaps.write('./maps'))
        .pipe(gulp.dest('dist/js'))
        .pipe(notify("Built JS!"));
});


gulp.task('serve:backend', function () {
    var devServerPort = process.env.PORT || 8000;
    process.env.PYTHONUNBUFFERED = 1;
    process.env.PYTHONDONTWRITEBITECODE = 1;
    spawn('python', ['manage.py', 'runserver', '0.0.0.0:' + devServerPort], {
        stdio: 'inherit'
    });
});

gulp.task('dev', ["sass", "scripts"], function() {
    gulp.start('serve:backend');
    gulp.watch('**/*.scss', ['sass']);
    gulp.watch('**/*.js', ['scripts']);
});

gulp.task("default", ["sass", "scripts"]);