var tfn = window.tfn || {};

jQuery(function($){
  tfn.wrapper = $("#tfn-app .partial");
  tfn.partial = tfn.wrapper.attr("data-partial");
  console.log(tfn.partial);
  switch(tfn.partial){
    case "initial":
      break;
    default:
  }
});