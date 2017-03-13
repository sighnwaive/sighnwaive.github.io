var gulp = require('gulp');
var subtree = require('gulp-subtree');
var clean = require('gulp-clean');
var package = require('./package.json');
 
gulp.task('deploy', function () {
    return gulp.src('./public/')
        .pipe(subtree({
		remote: 'origin',
		branch: 'gh-pages',
		message: 'Deploying v' + package.version
	}))
});
