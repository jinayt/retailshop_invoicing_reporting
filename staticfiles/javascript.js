$(".sidebar ul li").on('click', function(){
    console.log("Clicked: ", $(this).text());
      $('.sidebar ul li.active').removeClass('active');
      $(this).addClass('active');

  })
  $('.open-btn').on('click',function(){
    $('.sidebar').addClass('active');
})
$('.close-btn').on('click',function(){
    $('.sidebar').removeClass('active');
})