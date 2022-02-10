document.addEventListener('DOMContentLoaded', function(){

    new Glider(document.querySelector('.glider'), {
        slidesToScroll: 1,
        slidesToShow: 1,
        dragVelocity:1,
        draggable: true,
        dots: '.dots',
        arrows: {
            prev: '.glider-prev',
            next: '.glider-next'
        },
        responsive: [
            {
                // screens greater than >= 775px
                breakpoint: 600,
                settings: {
                    slidesToShow: 2,

                }
            },{
                // screens greater than >= 1024px
                breakpoint: 1024,
                settings: {
                    slidesToShow: 3,

                }
            }
        ]
    });
})

