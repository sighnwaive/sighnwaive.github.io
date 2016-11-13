var markdown = new showdown.Converter();

var html = $("#blogs-template").html();
console.log(html);
var blogTemplate = Handlebars.compile(html);

$(function(){
  $.ajax({
    url: 'https://dcbartlett-github-io.firebaseio.com/blogs.json',
    type: 'get',
    success: function (blogs) {
      $("#blogView").html(blogTemplate({blogs:blogs}));
    },
    error: function (XMLHttpRequest, textStatus, errorThrown) {
      console.log('error', errorThrown);
    }
  });
});

Handlebars.registerHelper('blogs', function(blogEntries) {
  var out = '<div id="blogs">';

  for (var blog in blogEntries) {
    out = out + '<div class="blog">' + markdown.makeHtml(blogEntries[i].body) + '</li>';
  }

  return out + '</div>';
});
