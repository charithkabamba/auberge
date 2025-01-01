var csrf = $('meta[name="csrf-token"]').attr('content');
var base_url = $('meta[name="base_url"]').attr('content');
var current_url = window.location.href;
var $document = $(document);

$(document).ready(function() {

  /* ======= Preloader ======= */
  $('.loader-container').delay('500').fadeOut(1000);

    $(window).keydown(function(event){
        if(event.keyCode == 13) {
          event.preventDefault();
          return false;
        }
    });
    if($("#map").length) {
        var lat = parseFloat($('.map-container #latitude').val());
        var lng = parseFloat($('.map-container #longitude').val());
        initMap('map', lat, lng);
    }

    $document.on('keyup', '#search', function (event) {
        $("#query").val($("#search").val());
        if (event.keyCode === 13) {
            $("#search-btn").click();
        }
    });

    var page = 1;
    $document.on('click', '#load-more', function () {
        var category_id = $('#category').val();
        var sort = $('#sort').val();
        page++;
        $.ajax({
            headers: {
                'X-CSRF-TOKEN': csrf
            },
            data: {
                category_id: category_id,
                sort: sort,
                _token: csrf
            },
            url: '?page=' + page,
            type: 'post',
        })
        .done(function(data){
            if(data.meta.current_page == data.meta.last_page){
                $('#load-more').hide();
            } else{
                $('#load-more').show();
            }
            $('.product-list').append(data.html);
        })
        .fail(function(jqXHR, ajaxOptions, throwError){
            alert('Server error');
        })
    });

    $document.on('change', '.filter-data', function () {
        var category_id = $('#category').val();
        var sort = $('#sort').val();
        page = 1;
        if (current_url == base_url +'/all-products') {
            var send_url = base_url +'/all-products?page=1';
        } else {
            var send_url = base_url +'/featured-products?page=1';
        }
        $.ajax({
            type: 'post',
            headers: {
                'X-CSRF-TOKEN': csrf
            },
            data: {
                category_id: category_id,
                sort: sort,
                _token: csrf
            },
            url: send_url,
            success: function (data) {
                $('.cat_name').html(data.category.name);
                $('.product-list').empty();
                if(data.meta.current_page == data.meta.last_page){
                    $('#load-more').hide();
                } else{
                    $('#load-more').show();
                }
                if(data.meta.data.length > 0)
                    $('.product-list').append(data.html);
                else
                    $('.product-list').append('<div class="col-lg-12 col-md-12"><div class="how-order-steps"><div class="how-order-icon"><i class="uil uil-shopping-basket"></i></div><h4>No Product Available</h4></div></div>');
            },
            error: function (data) {}
        })
    });

    var page_cat = 1;
    $document.on('click', '#load-more-categoty', function () {
        var sort = $('#sort').val();
        page_cat++;
        $.ajax({
            headers: {
                'X-CSRF-TOKEN': csrf
            },
            data: {
                sort: sort,
                _token: csrf
            },
            url: '?page=' + page_cat,
            type: 'post',
        })
        .done(function(data){
            if(data.meta.current_page == data.meta.last_page){
                $('#load-more-categoty').hide();
            } else{
                $('#load-more-categoty').show();
            }
            $('.product-list').append(data.html);
        })
        .fail(function(jqXHR, ajaxOptions, throwError){
            alert('Server error');
        })
    });

    $document.on('change', '.filter-data-category', function () {
        var sort = $('#sort').val();
        page_cat = 1;
        $.ajax({
            type: 'post',
            headers: {
                'X-CSRF-TOKEN': csrf
            },
            data: {
                sort: sort,
                _token: csrf
            },
            url: '?page=' + page_cat,
            success: function (data) {
                $('.cat_name').html(data.category.name);
                $('.product-list').empty();
                if(data.meta.current_page == data.meta.last_page){
                    $('#load-more-categoty').hide();
                } else{
                    $('#load-more-categoty').show();
                }
                if(data.meta.data.length > 0)
                    $('.product-list').append(data.html);
                else
                    $('.product-list').append('<div class="col-lg-12 col-md-12"><div class="how-order-steps"><div class="how-order-icon"><i class="uil uil-shopping-basket"></i></div><h4>No Product Available</h4></div></div>');
            },
            error: function (data) {}
        })
    });

    // single item
    $document.on('change', '.item-detail', function () {
        var product_id = $('#product_id').val();
        var detail_index = $(this).attr('id');
        var qty = $('.qtyOf-'+product_id).val();
        $('.item-index-id').val(detail_index);
        $.ajax({
            type: 'post',
            headers: {
                'X-CSRF-TOKEN': csrf
            },
            data: {
                product_id: product_id,
                detail_index: detail_index,
                qty: qty,
                _token: csrf
            },
            url: base_url +'/get-product-details',
            success: function (data) {
                $('.product-sell_price').html(data.price);
                $('.product-fake_price').html(data.fake_price);
            },
            error: function (data) {}
        })
    });

    $document.on('change', '.item-qty', function () {
        var product_id = $('#product_id').val();
        var detail_index = $('.item-index-id').val();
        var qty = $('.qtyOf-'+product_id).val();
       
        $.ajax({
            type: 'post',
            headers: {
                'X-CSRF-TOKEN': csrf
            },
            data: {
                product_id: product_id,
                detail_index: detail_index,
                qty: qty,
                _token: csrf
            },
            url: base_url +'/get-product-details',
            success: function (data) {
                $('.product-sell_price').html(data.price);
                $('.product-fake_price').html(data.fake_price);
                $('.qtyOf-'+product_id).val(qty);
            },
            error: function (data) {}
        })
    });
    
    // cart
    $document.on('change', '.cart-item-detail', function () {
        var product_id = $(this).attr("data-id");
        var detail_index = $(this).attr("data-index-id");
        $(this).closest('.cart-radio').find("input[name='cart-item-detail-index-id']").val(detail_index);
        var qty = $(this).closest('.cart-text').find("input[name='quantity']").val();
        $.ajax({
            type: 'post',
            headers: {
                'X-CSRF-TOKEN': csrf
            },
            data: {
                product_id: product_id,
                detail_index: detail_index,
                qty:qty,
                _token: csrf
            },
            url: base_url +'/get-product-details',
            success: function (data) {
                $('.sell_price_'+product_id).html(data.price);
                $('.fake_price_'+product_id).html(data.fake_price);
                $('.off_'+product_id).html(data.off);

                $('.cart-main-total').html(data.cart_total);
                $('.cart-saving-total').html(data.cart_saving);
                $('.cart-final-total').html(data.cart_total_with_delivery);
                $('.cart-discount').html(data.discount);
            },
            error: function (e) {}
        })
    });

    $document.on('change', '.cart-qty', function () {
        var product_id = $(this).closest(".cart-text").find("input[name='cart-item-id']").val();
        var detail_index = $(this).closest('.cart-text').find("input[name='cart-item-detail-index-id']").val();
        var qty = $(this).closest("input[name='quantity']").val();
       
        $.ajax({
            type: 'post',
            headers: {
                'X-CSRF-TOKEN': csrf
            },
            data: {
                product_id: product_id,
                detail_index: detail_index,
                qty: qty,
                _token: csrf
            },
            url: base_url +'/get-product-details',
            success: function (data) {
                $('.sell_price_'+product_id).html(data.price);
                $('.fake_price_'+product_id).html(data.fake_price);
                $('.off_'+product_id).html(data.off);
                $('.qtyOf-'+product_id).val(qty);

                $('.cart-main-total').html(data.cart_total);
                $('.cart-saving-total').html(data.cart_saving);
                $('.cart-final-total').html(data.cart_total_with_delivery);
            },
            error: function (data) {}
        })
    });

    $document.on('click', '.add-to-cart', function() {
        var item_id = $(this).attr("data-id");
        var qty = $(this).closest(".qty-cart").find("input[name='quantity']").val();
        var sell_price = $(this).closest(".product-text-dt").children(".product-price").children(".sell_price").html();
        var fake_price = $(this).closest(".product-text-dt").children(".product-price").children(".line-through").children(".fake_price").html();
        var detail_index = 0;
        if (qty == 0) {
            qty = 1;
        }
        
        if($(this).hasClass("single-page")){
            qty = $(this).closest(".cart-item").find("input[name='quantity']").val();
            sell_price = $(this).closest(".cart-text").children(".product-price").children(".sell_price").html();
            fake_price = $(this).closest(".cart-text").children(".product-price").children(".line-through").children(".fake_price").html();
        }
        if($(this).hasClass("single-page-product")){
            qty = $(this).closest(".product-group-dt").find("input[name='quantity']").val();
            sell_price = $(this).closest(".product-group-dt").children("#product-price").children(".li-sell-price").children(".color-discount").children("#price").children(".product-sell_price").html();
            fake_price = $(this).closest(".product-group-dt").children("#product-price").children(".li-fake-price").children(".mrp-price").children("#fake_price").children(".product-fake_price").html();
            detail_index = $(this).closest(".product-group-dt").find("input[name='item-index-id']").val();
            console.log($(this).hasClass("add-cart"));
            if($(this).hasClass("add-cart")){
                $(this).removeClass("add-cart");
                $(this).addClass("remove-cart");
                $(this).children('.text-cart').html("Remove from Cart");
            } else {
                $(this).addClass("add-cart");
                $(this).removeClass("remove-cart");
                $(this).children('.text-cart').html("Add to Cart");
            }
        }
        var this1 = $(this);
        
        $.ajax({
            type: 'post',
            headers: {
                'X-CSRF-TOKEN': csrf
            },
            data: {
                item_id: item_id,
                qty: qty,
                sell_price: sell_price,
                fake_price: fake_price,
                detail_index: detail_index,
                _token: csrf
            },
            url: base_url + '/add-to-cart',
            success: function (data) {
                // remove
                if (this1.hasClass('pri-color')) {
                    $('.cart-'+item_id).removeClass('pri-color');
                    $('.qtyOf-'+item_id).val(qty);
                }
                // add
                else {
                    $('.cart-'+item_id).addClass('pri-color');
                    $('.qtyOf-'+item_id).val(qty);
                }
                $("#cart").html(data.data);
                $('.cart-item-count').html(data.total_item);
            },
            error: function (err) {
                Swal.fire({
                    icon: 'error',
                    title: 'Oops...',
                    text: err.responseJSON.msg
                })
            }
        })
	});

    $document.on('click', '.cart-close-btn', function(e) {
        var item_id = $(this).attr("data-id");
        $('.cart-'+item_id).removeClass('pri-color');
        $(this).closest(".cart-item").remove();
        $('.qtyOf-'+item_id).val(1);
        var hasClass = 0;
        if($(this).hasClass("checkout-cart-close-btn")){
            hasClass = 1;
        }

        $.ajax({
            type: 'post',
            headers: {
                'X-CSRF-TOKEN': csrf
            },
            data: {
                item_id: item_id,
                _token: csrf
            },
            url: base_url + '/remove-from-cart',
            success: function (data) {
                $('.cart-item-count').html(data.total_item);
                $('.cart-main-total').html(data.total.cart_total);
                $('.cart-saving-total').html(data.total.cart_saving);
                $('.cart-discount').html(data.total.discount);
                $('.cart-final-total').html(data.total.cart_total_with_delivery);
                if(hasClass)
                {
                    if(current_url == base_url+'/checkout')
                    {
                        $("#cart").html(data.data);
                    }
                } else {
                    $('.cart-item-'+item_id).remove();
                }
                if(data.total_item  >= 0)
                {
                    $('#collapseThree').addClass("display-none");
                }
            },
            error: function (data) {}
        })
	});

    $document.on('click', '.wishlist-btn', function(e) {
        e.preventDefault();
        e.stopPropagation();

        var product_id = $(this).attr("data-product");
        toggleWishlist(this, product_id);

        let wishlist_count = parseInt($('.noti_count1').html());
        if($(this).hasClass('liked')){
            if (wishlist_count > 0) {
                wishlist_count--;
            }
        } else {
            wishlist_count++;
        }
        $('.noti_count1').html(wishlist_count);
    });
    
    // $document.on('click','.like-icon, .like-button', function(e) {
	// 	e.preventDefault();
    //     var item_id = $(this).attr("data-id");
    //     var wishlist_count = parseInt($('.noti_count1').html());
    //     // Dislike
    //     if ($(this).hasClass('liked')) {
    //         Swal.fire({
    //             title: 'Are you sure?',
    //             text: "You want to remove this item from wishlist?",
    //             icon: 'warning',
    //             showCancelButton: true,
    //             confirmButtonColor: '#3085d6',
    //             cancelButtonColor: '#d33',
    //             confirmButtonText: 'Yes, remove it!'
    //         }).then((result) => {
    //             if (result.value) {
    //                 $.ajax({
    //                     method: "GET",
    //                     url: base_url+'/wishlist/remove/'+item_id,
    //                     success: function (result) {
    //                         $('.like-'+item_id).removeClass('liked');
    //                         wishlist_count--;
    //                         $('.noti_count1').html(wishlist_count);
    //                     },
    //                     error: function (err) {
    //                         Swal.fire({
    //                             icon: 'error',
    //                             title: 'Oops...',
    //                             text: 'This record is conntect with another data!'
    //                         })
    //                     }
    //                 });
    //             }
    //         })
    //     }
    //     // like
    //     else {
    //         $.ajax({
    //             headers: {
    //                 'XCSRF-TOKEN': csrf
    //             },
    //             type:"GET",
    //             url: base_url+'/wishlist/'+item_id,
    //             success: function(result){
    //                 if (result.success == false) {
    //                     window.location.href = base_url+'/signin';
    //                 } else {
    //                     $('.like-'+item_id).addClass('liked');
    //                     wishlist_count++;
    //                     $('.noti_count1').html(wishlist_count);
    //                 }
    //             },
    //             error: function(err){
    //             }
    //         });
    //     }
	// });

    $document.on('click', '.code-apply-btn', function(e) {
        var code = $('#input-promocode').val();
        if(code == "") {
            Swal.fire('Enter a valid coupon code');
        } else {
            $.ajax({
                method: "GET",
                url: base_url+'/checkCoupon/'+code,
                success: function (result) {
                    if (result.success) {
                        // here
                        $('.cart-discount').html(result.data.cart_discount);
                        $('.cart-main-total').html(result.data.cart_total);
                        $('.cart-final-total').html(result.data.cart_total_with_delivery);
                        Swal.fire({
                            icon: 'success',
                            title: result.msg,
                            showConfirmButton: false,
                            timer: 1500
                        })
                        setTimeout(() => {
                            window.location.reload();
                        }, 700);
                    } else {
                        Swal.fire({
                            icon: 'error',
                            title: 'Oops...',
                            text: result.msg
                        })
                    }
                },
                error: function (err) {
                    Swal.fire({
                        icon: 'error',
                        title: 'Oops...',
                        text: 'Something went wrong'
                    })
                }
            });
        }
    });

    $document.on('change', '.address-types', function(e) {
        var address_id = $(this).val();
        $.ajax({
            headers: {
                'XCSRF-TOKEN': csrf
            },
            type:"GET",
            url: base_url + '/profile/addressView/' + address_id,
            success: function(result){
                $("#soc_name_show").val(result.soc_name);
                $("#street_show").val(result.street);
                $("#pincode_show").val(result.zipcode);
                $("#city_show").val(result.city);
            },
            error: function(err){}
        });
    });

    $document.on('click', 'input[name="payment_type"]', function(e) {
        var $value = $(this).attr('value');
        $('.return-departure-dts').slideUp();
        $('[data-method="' + $value + '"]').slideDown();
        if($value == "STRIPE"){
            $("#holdername").prop('required',true);
            $("#cardnumber").prop('required',true);
            $("#expire_month").prop('required',true);
            $("#expire_year").prop('required',true);
            $("#cvv").prop('required',true);
        } else {
            $("#holdername").prop('required',false);
            $("#cardnumber").prop('required',false);
            $("#expire_month").prop('required',false);
            $("#expire_year").prop('required',false);
            $("#cvv").prop('required',false);
        }
    });

    $document.on('change', '.payment_type', function(e) {
        $('#paypal-button-container').html(''); 
		$('.paypal-button-section').hide();
        if(this.value == "PAYPAL")
        {
            $('#form_submit').attr('disabled', true);
			paypal_sdk.Buttons({
                createOrder: function(data, actions) {
                    return actions.order.create({
                        purchase_units: [{
                            amount: {
                                value: $('.cart-final-total').html()
                            }
                        }]
                    });
                },
                onApprove: function(data, actions) {
                    return actions.order.capture().then(function(details) {                         
                        $('#payment_token').val(details.id);
                        $('#form_submit').attr('disabled', false);
                    });
                }
            }).render('#paypal-button-container');

            $('.paypal-button-section').show(500);
        } else if(this.value == "RAZOR") {
            $('#form_submit').attr('disabled', true);			
            var options = {
                key: $('#razor_key').val(),
                amount: $('.cart-final-total').html() * 100,
                name: 'CodesCompanion',
                description: 'test',
                image: 'https://i.imgur.com/n5tjHFD.png',
                handler: demoSuccessHandler
            }
            window.r = new Razorpay(options);        
            r.open();
        } else if(this.value == "PAYSTACK"){
            var paymentForm = document.getElementById('checkout-form');
            if(paymentForm != '' && paymentForm != null)
            {
                payWithPaystack();
            }
        } else {
            $('#form_submit').attr('disabled', false);
        }
    });

    $document.on('click', '.last-step', function(e) {
        var selected = $(".product-radio input[name='address_id']:checked").val();
        var cart_item = $('.cart-item-count').html();
        var ready = 1;
        if (typeof selected == 'undefined'){
            ready = 0;
            Swal.fire({
                icon: 'error',
                title: 'Oops...',
                text: "Please select address"
            })
        }
        if(cart_item <= 0){
            ready = 0;
            Swal.fire({
                icon: 'error',
                title: 'Oops...',
                text: "Please select product to purchase"
            })
        }
        if (ready) {
            $('#collapseThree').removeClass("display-none");
        }
    });
});

function demoSuccessHandler(transaction) {	
	$('#payment_token').val(transaction.razorpay_payment_id)
	$('#form_submit').attr('disabled', false);
}

function payWithPaystack()
{
    var handler = PaystackPop.setup(
    {
        key: $("#paystack_public_key").val(),
        email: $("#auth_email").val(),
        amount: $('.cart-final-total').html() * 100,
        currency: 'ZAR',
        ref: Math.floor(Math.random() * (999999 - 111111)) + 999999,
        callback: function (response)
        {
            if(response.status == "success"){
                $('#payment_token').val(response.reference);
                $("#checkout-form").submit().delay( 800 );
            }
        },
        onClose: function ()
        {
            alert('Transaction was not completed, window closed.');
        },
    });
    handler.openIframe();
}

// function removeFromWishlist(item_id) {
//     Swal.fire({
//         title: 'Are you sure?',
//         text: "You want to remove this item from wishlist?",
//         icon: 'warning',
//         showCancelButton: true,
//         confirmButtonColor: '#3085d6',
//         cancelButtonColor: '#d33',
//         confirmButtonText: 'Yes, remove it!'
//     }).then((result) => {
//         if (result.value) {
//             $.ajax({
//                 method: "GET",
//                 url: base_url+'/wishlist/remove/'+item_id,
//                 success: function (result) {
//                     setTimeout(() => {
//                         window.location.reload();
//                     }, 700);
//                     Swal.fire({
//                         icon: 'success',
//                         title: 'Deleted!',
//                         text: 'Item removed successfully.',
//                         showConfirmButton: false,
//                     })
//                 },
//                 error: function (err) {
//                     Swal.fire({
//                         icon: 'error',
//                         title: 'Oops...',
//                         text: 'This record is conntect with another data!'
//                     })
//                 }
//             });
//         }
//     })
// }

// Wishlist functions
function toggleWishlist(element, productId) {
    fetch('/users/api/wishlist/toggle/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({
            product_id: productId
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            Swal.fire('Error', data.error, 'error');
        } else {
            element.classList.toggle('liked');
            
            // If we're on the wishlist page, remove the item
            if (window.location.pathname.includes('/dashboard/wishlist/')) {
                const productCard = element.closest('.col-lg-3');
                if (productCard) {
                    productCard.remove();
                    // Check if wishlist is empty
                    if (document.querySelectorAll('.product-item').length === 0) {
                        window.location.reload();
                    }
                }
            } else {
                // Show success message on other pages
                Swal.fire({
                    icon: 'success',
                    title: 'Success',
                    text: data.message,
                    timer: 1500
                });
            }
        }
    });
}

// Add to cart function
function addToCart(productId, quantity = 1) {
    fetch('/cart/api/add/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({
            product_id: productId,
            quantity: quantity
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            Swal.fire('Error', data.error, 'error');
        } else {
            Swal.fire({
                icon: 'success',
                title: 'Success',
                text: 'Item added to cart',
                timer: 1500
            });
            updateCartCount(data.cart_total);
        }
    });
}

// Product sorting
document.addEventListener('DOMContentLoaded', function() {
    const sortDropdown = document.querySelector('.vchrt-dropdown');
    if (sortDropdown) {
        sortDropdown.addEventListener('change', function(e) {
            const sortValue = e.target.value;
            const currentUrl = new URL(window.location.href);
            currentUrl.searchParams.set('sort', sortValue);
            window.location.href = currentUrl.toString();
        });
    }
});