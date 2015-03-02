var tfn = window.tfn || {};

jQuery(function($){
  tfn.wrapper = $("#tfn-app .partial");
  tfn.partial = tfn.wrapper.attr("data-partial");
  tfn.home_category = tfn.home_category || "all";
  //router
  switch(tfn.partial){
    case "home":
      tfn.home();
      break;
    default:
  }
  
  //click events
  $('.tfn-header .logo').click(function(){
    tfn.home_category = $(this).attr("data-selection");
    tfn.home();
  });
  
});

tfn.home = function(){
  var fake_rundown_posts = [
    {
      title: "This is a LCS Rundown podcast episode",
      content: "This is the new website and here is the place an excerpt would go to show the general details of this post!",
      show: "rundown",
      hosts: ["motgnarom", "optimustom", "tsepha", "crediblemushroom", "cerealbawkz"],
      tags: ["esports", "pro play", "strategy", "poppywatch 2015", "guest", "NME gaming"],
      category: "podcast",
      video_url: "http://youtu.be/8x1oHRd46QM",
      image_url: "http://imgur.com/gallery/eRcR1fQ",
      stitcher_url: "http://app.stitcher.com/splayer/f/45272/36934480",
      itunes_url: "https://itunes.apple.com/us/podcast/lcs-podcast/id822327403"
    },
    {
      title: "This is a LCS Rundown podcast episode",
      content: "This is the new website and here is the place an excerpt would go to show the general details of this post!",
      show: "LCS Rundown",
      hosts: ["motgnarom", "optimustom", "tsepha", "crediblemushroom", "cerealbawkz"],
      tags: ["esports", "pro play", "strategy", "poppywatch 2015", "guest", "NME gaming"],
      category: "podcast",
      video_url: "http://youtu.be/8x1oHRd46QM",
      image_url: "http://imgur.com/gallery/eRcR1fQ",
      stitcher_url: "http://app.stitcher.com/splayer/f/45272/36934480",
      itunes_url: "https://itunes.apple.com/us/podcast/lcs-podcast/id822327403"
    }
  ];
  var fake_proper_posts = [
    {
      title: "This is a Tforce proper podcast episode",
      content: "This is the new website and here is the place an excerpt would go to show the general details of this post!",
      show: "proper",
      hosts: ["pwnophobia", "declawd", "daysuntold", "chirajaeden", "punchinjello"],
      tags: ["patch 5.2", "mechanics", "wave manipulation", "mailbag", "top lane", "dyrus"],
      category: "podcast",
      video_url: "http://youtu.be/8x1oHRd46QM",
      image_url: "http://imgur.com/gallery/eRcR1fQ",
      stitcher_url: "http://app.stitcher.com/splayer/f/27428/36930238",
      itunes_url: "https://itunes.apple.com/us/podcast/trinity-force-podcast-league/id485769640"
    },
    {
      title: "This is a Tforce proper podcast episode",
      content: "This is the new website and here is the place an excerpt would go to show the general details of this post!",
      show: "proper",
      hosts: ["pwnophobia", "declawd", "daysuntold", "chirajaeden", "punchinjello"],
      tags: ["patch 5.2", "mechanics", "wave manipulation", "mailbag", "top lane", "dyrus"],
      category: "podcast",
      video_url: "http://youtu.be/8x1oHRd46QM",
      image_url: "http://imgur.com/gallery/eRcR1fQ",
      stitcher_url: "http://app.stitcher.com/splayer/f/27428/36930238",
      itunes_url: "https://itunes.apple.com/us/podcast/trinity-force-podcast-league/id485769640"
    }
  ];
  var post_card = tfn.wrapper.find('.main__posts .post.template').clone();
  var body = tfn.wrapper.find('.main__posts');
  body.find('.post.cloned').remove();
  var target_posts;
  if(tfn.home_category == "all"){
    target_posts = fake_proper_posts;
  }
  
  switch(tfn.home_category){
    case "all":
      target_posts = fake_proper_posts.concat(fake_rundown_posts);
      fill_in_posts(target_posts);
      break;
    case "home":
      target_posts = fake_proper_posts.concat(fake_rundown_posts);
      fill_in_posts(target_posts);
      break;
    case "rundown":
      target_posts = fake_rundown_posts;
      fill_in_posts(target_posts);
      break;
    case "proper":
      target_posts = fake_proper_posts;
      fill_in_posts(target_posts);
      break;
    default:
      body.append("<span class=\"post cloned\">No posts are available for this category.</span>");
  }
  
  function fill_in_posts(target_posts){
    for(var i=0;i<target_posts.length;i++){
      var post = target_posts[i];
      var temp_card = post_card.clone().removeClass("template").addClass("cloned");
      temp_card.find('.post-title').html(post.title);
      temp_card.find('.post-content').html(post.content);
      temp_card.find('.post-show').html(post.show);
      var hosts_string = "Hosted by:";
      for(var j=0;j<post.hosts.length;j++){
        hosts_string = hosts_string + " " + post.hosts[j];
      }
      temp_card.find('.hosted-by').html(hosts_string);
      temp_card.find('.post-content').html(post.content);
      var tags_string = "Tags:";
      for(var k=0;k<post.tags.length;k++){
        tags_string = tags_string + " <a href=\"#\">" + post.tags[k] + "</a>";
      }
      temp_card.find('.post-tags').html(tags_string);
      body.append(temp_card);
    }
  }
}
















