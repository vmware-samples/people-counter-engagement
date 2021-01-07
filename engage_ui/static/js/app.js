
/* 
Copyright 2019-2020 VMware, Inc.

SPDX-License-Identifier: BSD-2-Clause
*/
$(document).ready(function(){
    var slideIndex = 1;
    var deviceCount = 0;
    showSlides(slideIndex);
    
    // Next/previous controls
    function plusSlides(n) {
      showSlides(slideIndex += n);
    }
    
    // Thumbnail image controls
    function currentSlide(n) {
      showSlides(slideIndex = n);
    }
    
    function showSlides(n) {
      if( deviceCount > 0){
        console.log("Slide index: " + n);
        var slides = $(".mySlides");
        var dots = $(".dot");
        if (n > slides.length) {
            slideIndex = 1;
        }
        if (n < 1) {
            slideIndex = slides.length;
        }
        slides.each(function(){
            $(this).hide();
        });
        dots.each(function(){
            $(this).removeClass('active').addClass('');
        });
        slides[slideIndex-1].style.display = "block";
        dots[slideIndex-1].className += " active";
      }
    }

    // Image logic
    $( "#nextImage" ).click(function(){
        plusSlides(1);
    });
    
    $( "#previousImage" ).click(function(){
        plusSlides(-1);
    });
    
    /**
     * Add a 4 new HTML element to the page to show a new item in the slideshow.
     * One element has 2 child elements: img and div. The img hold the image source to
     * display on the page and the div holds the description of the image. The image
     * source and description are in the parameter metadata. The other HTML element
     * is a span that show as a dot at the bottom of the slideshow.
     * @param  {String} id The id you for new parent HTML element holding the image information
     * @param  {Object} metadata Image information
     */
    function addSlide(id, metadata){
        deviceCount += 1;
        var stringCount = deviceCount.toString()
        var image = metadata.displayPath;
        var peopleCount = metadata.analysisMetadata.results.count;
        var timestamp = new Date(metadata.creationTimestamp*1000).toUTCString() 
        var slideDetails = `
            &emsp;&emsp;&emsp;&emsp;Device ID: ${ metadata.deviceID }<br> 
            Creation Time: ${timestamp}<br>
        `;
        var newElement = `
        <div id="`+ id + `" class="mySlides fade" data-index="${stringCount}">
            <div class="slide-details">${slideDetails}</div>
            <div class="count-title">Count</div>
            <div class="count-value">${peopleCount}</div>
            <img src="${image}" class="slide-images">
          </div>
        `;
        $('#slides').append(newElement);
        $( "<span/>", {
            "class": "dot",
            "data-index": stringCount,
            click: function() {
                var imageIndex = $(this).attr('data-index');
                index = parseInt(imageIndex);
                currentSlide(index);
            }
          }).appendTo( "#dots-menu" );
    }

    /**
     * Update an image in the slideshow along with it's description. If the image with the
     * given id is not found, it will create it.
     * @param  {String} id The id you for parent HTML element holding the image information
     * @param  {Object} metadata Image information
     */
    function updateSlide(id, metadata){
        if($('#' + id).length){
            var image = metadata.displayPath;
            var peopleCount = metadata.analysisMetadata.results.count;
            var timestamp = new Date(metadata.creationTimestamp*1000).toUTCString() 
            var slideDetails = `
                &emsp;&emsp;&emsp;&emsp;Device ID: ${ metadata.deviceID }<br> 
                Creation Time: ${timestamp}<br>
            `;
            $('#' + id + ' > img').attr("src", image);
            $('#' + id + ' > .count-value').text(peopleCount);
            $('#' + id + ' > .slide-details').html(slideDetails);
        }else{
            addSlide(id, metadata);
        }
    }

    function toggleVisible(){
        var message = $('#no-data-message');
        if(message.is(':visible')){
            message.hide();
        }else{
            message.show();
        }
        
        var controls = $('.prev, .next');
        if(controls.is(':visible')){
            controls.hide();
        }else{
            controls.show();
        }
    }

    // server connection information
    baseURL = 'http://' + document.domain + ':' + location.port;
    var socket = io.connect(baseURL + '/test');

    // get list of all available images from devices
    $.ajax({
        url: baseURL + '/api/v1.0/devices',
        type: "GET",
        contentType: "application/json",
        dataType: 'json',
        success: function(result){
            console.log(result);
            var count = 0;
            Object.keys(result).forEach(function(key){
                addSlide(key,result[key]);
                count++;
            });
            if (count > 0){
                showSlides(1);
                toggleVisible();
            }
        },
        error: function(error){
            console.log(`Error ${error}`);
        }
    });

    // receive updates about images captured by devices
    socket.on('devicesupdates', function(msg) {
        updateSlide(msg.deviceID, msg);
        showSlides(slideIndex);
        if($('#no-data-message').is(':visible')){
            toggleVisible();
        }
    });
});