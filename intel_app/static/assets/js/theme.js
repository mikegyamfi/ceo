/* Sticky Navigation */
$(function() {
  
  var sticky = $('.sticky');
  var contentOffset;
  var nav_height;
  
  if (sticky.length) {
    
    if ( sticky.data('offset') ) {
      contentOffset = sticky.data('offset');
    }
    else {
      contentOffset = sticky.offset().top;
    }
    nav_height = sticky.height();
  }
  
  var scrollTop = $(window).scrollTop();
  var window_height = $(window).height();
  var doc_height = $(document).height();
  
  $(window).bind('resize', function() {
    scrollTop = $(window).scrollTop();
    window_height = $(window).height();
    doc_height = $(document).height();
    navHeight();
  });
  
  $(window).bind('scroll', function() {
    stickyNav();
  });
  
  function navHeight() {
    sticky.css('max-height', window_height + 'px');
  }
  
  function stickyNav() {
    scrollTop = $(window).scrollTop();
    if (scrollTop > contentOffset) {
      sticky.addClass('fixed');
    }
    else {
      sticky.removeClass('fixed');
    }
  }
  
});

$('document').ready(function() {
  var nav_height = 70;
  
  $("a[data-role='smoothscroll']").click(function(e) {
    e.preventDefault();
    
    var position = $($(this).attr("href")).offset().top - nav_height;
    
    $("body, html").animate({
      scrollTop: position
    }, 1000 );
    return false;
  });
});

$('document').ready(function() {
  // Back to top
  var backTop = $(".back-to-top");
  
  $(window).scroll(function() {
    if($(document).scrollTop() > 400) {
      backTop.css('visibility', 'visible');
    }
    else if($(document).scrollTop() < 400) {
      backTop.css('visibility', 'hidden');
    }
  });
  
  backTop.click(function() {
    $('html').animate({
      scrollTop: 0
    }, 1000);
    return false;
  });
});


$('document').ready(function() {
  
  // Loader
  $(window).on('load', function() {
    $('.loader-container').fadeOut();
  });
  
  // Tooltips
  $('[data-toggle="tooltip"]').tooltip();
  
  // Popovers
  $('[data-toggle="popover"]').popover();
  
  // Page scroll animate
  new WOW().init();
});

$('document').ready(function() {
  $('#testimonials').owlCarousel({
    items: 1,
    loop: true,
    autoplay: true,
    autoplayHoverPause: true,
    animateOut: 'fadeOut',
    animateIn: 'fadeIn',
  });
});


/*
 *  Counter
 *
 *  Require(" jquery.animateNumber.min.js ", " jquery.waypoints.min.js ")
 */
$(document).ready(function() {
  var counterInit = function() {
    if ( $('.counter-section').length > 0 ) {
      $('.counter-section').waypoint( function( direction ) {

        if( direction === 'down' && !$(this.element).hasClass('animated') ) {

          var comma_separator_number_step = $.animateNumber.numberStepFactories.separator(',')
          $('.number').each(function(){
            var $this = $(this),
              num = $this.data('number');
            $this.animateNumber(
              {
                number: num,
                numberStep: comma_separator_number_step
              }, 5000
            );
          });
          
        }

      } , { offset: '95%' } );
    }

  }

  counterInit();
});


$(document).ready(function () {
  // Increase quantity
  $(document).on("click", ".inc-btn", function (e) {
    e.preventDefault();
    let $parent = $(this).closest(".product-data");
    let value = parseInt($parent.find(".qty-val").val()) || 0;
    if (value < 10) {
      $parent.find(".qty-val").val(value + 1);
    }
  });

  // Decrease quantity
  $(document).on("click", ".dec-btn", function (e) {
    e.preventDefault();
    let $parent = $(this).closest(".product-data");
    let value = parseInt($parent.find(".qty-val").val()) || 0;
    if (value > 1) {
      $parent.find(".qty-val").val(value - 1);
    }
  });

  // Add to Cart
  $(document).on("click", ".addToCart", function (e) {
    e.preventDefault();

    let $parent = $(this).closest(".product-data");
    let product_id = $parent.find(".prod_id").val();
    let product_qty = $parent.find(".qty-val").val();
    let color_id = $parent.find("select[name=color]").val();
    let size_id = $parent.find("select[name=size]").val();
    let token = $("input[name=csrfmiddlewaretoken]").val();

    $.ajax({
      method: "POST",
      url: "/add-to-cart/",
      data: {
        product_id: product_id,
        product_qty: product_qty,
        color_id: color_id,
        size_id: size_id,
        csrfmiddlewaretoken: token,
      },
      success: function (response) {
        Toastify({
          text: response.status,
          duration: 5000,
        }).showToast();
      },
    });
  });

  // Update quantity in cart
  $(document).on("click", ".changeQty", function (e) {
    e.preventDefault();

    let $parent = $(this).closest(".product-data");
    let product_id = $parent.find(".prod_id").val();
    let product_qty = $parent.find(".qty-val").val();
    let color_id = $parent.find(".color_id").val();
    let size_id = $parent.find(".size_id").val();
    let token = $("input[name=csrfmiddlewaretoken]").val();

    $.ajax({
      method: "POST",
      url: "/update-cart",
      data: {
        product_id: product_id,
        product_qty: product_qty,
        color_id: color_id,
        size_id: size_id,
        csrfmiddlewaretoken: token,
      },
      success: function (response) {
        Toastify({
          text: response.status,
          duration: 5000,
        }).showToast();
      },
    });
  });

  // Delete item from cart
  $(document).on("click", ".delete-cart-item", function (e) {
    e.preventDefault();

    let $parent = $(this).closest(".product-data");
    let product_id = $parent.find(".prod_id").val();
    let color_id = $parent.find(".color_id").val();
    let size_id = $parent.find(".size_id").val();
    let token = $("input[name=csrfmiddlewaretoken]").val();

    $.ajax({
      method: "POST",
      url: "/delete-cart-item",
      data: {
        product_id: product_id,
        color_id: color_id,
        size_id: size_id,
        csrfmiddlewaretoken: token,
      },
      success: function (response) {
        Toastify({
          text: response.status,
          duration: 5000,
        }).showToast();
        $(".cart_data").load(location.href + " .cart_data");
      },
    });
  });
});

