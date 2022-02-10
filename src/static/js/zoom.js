document.addEventListener('DOMContentLoaded',()=>{

    function zoomImage(e) {
        const pathname = e.target.nextElementSibling.value;
        document.body.insertAdjacentHTML('beforeend',`<div class="zoom"><img src=${pathname}><i class="far fa-times-circle closebtn"></i></img> </div>`)
        document.querySelector('.zoom').addEventListener('click', removeZoom);
    }

    function removeZoom() {
        document.querySelector('.zoom').remove();
    }

    const cardItems = document.querySelectorAll('.category-card-item');
    cardItems.forEach((item)=>{
        item.children[0].addEventListener('click', zoomImage)
    })
});
