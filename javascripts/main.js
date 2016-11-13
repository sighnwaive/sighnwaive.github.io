var markdown = new showdown.Converter();

var html = $("#blogs-template").html();
console.log(html);
var blogTemplate = Handlebars.compile(html);

$(function(){
  $.ajax({
    url: 'https://dcbartlett-github-io.firebaseio.com/blogs.json',
    type: 'get',
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
