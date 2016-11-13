var markdown = new showdown.Converter();

var blogTemplate = Handlebars.compile($("#blogs-template").html());

$(function(){
  $.ajax({
    url: 'http://ds151697.mlab.com:51697/dcbartlett_github_io/blogs',
    type: 'get',
    dataType: 'jsonp',
    jsonp: 'jsonp', // mongod is expecting the parameter name to be called "jsonp"
    success: function (data) {
      console.log('success', data);
    },
    error: function (XMLHttpRequest, textStatus, errorThrown) {
      console.log('error', errorThrown);
    }
  });
});

// $("#blogView").html(blogTemplate());

Handlebars.registerHelper('blogs', function(blogEntries) {
  var out = '<div id="blogs">';

  for(var i=0, l=blogEntries.length; i<l; i++) {
    out = out + '<div class="blog">' + markdown.makeHtml(blogEntries[i].body) + '</li>';
  }

  return out + '</div>';
});
