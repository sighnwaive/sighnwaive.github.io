var gulp = require('gulp');
var subtree = require('gulp-subtree');
 
gulp.task('deploy', function () {
    return gulp.src('./public/')
        .pipe(subtree())
});
