document.addEventListener('DOMContentLoaded',()=>{

    const element = document.querySelector('.main-img-tabs');
    let dragging = false;
    let isMouseMove = false;

    //JSON.parse();
    let pos = { top: 0, left: 0, x: 0, y: 0 };
    function transformScroll(event) {
        if (!event.deltaY) {
            return;
        }

        event.currentTarget.scrollLeft += event.deltaY + event.deltaX;
        event.preventDefault();
    }

    const mouseDownHandler = function(e) {
        pos = {
            left: element.scrollLeft,
            top: element.scrollTop,
            x: e.clientX,
            y: e.clientY,
        };
        dragging = true;
        element.style.cursor = 'grabbing';
        element.style.userSelect = 'none';
        document.addEventListener('mousemove', mouseMoveHandler);
        document.addEventListener('mouseup', mouseUpHandler);
    };

    const mouseMoveHandler = function(e) {
        if(dragging){
            // How far the mouse has been moved
            const dx = e.clientX - pos.x;
            const dy = e.clientY - pos.y;
            isMouseMove = true;
            // Scroll the element
            element.scrollTop = pos.top - dy;
            element.scrollLeft = pos.left - dx;
        }
    };

    const mouseUpHandler = function(e) {
        dragging = false;
        element.style.cursor = 'grab';
        element.style.removeProperty('user-select');
        localStorage.setItem('scroll',JSON.stringify(element.scrollLeft));
    };
    element.addEventListener('click', (e)=>{
        if(isMouseMove) e.preventDefault();
        isMouseMove = false;
    })
    element.addEventListener('wheel', transformScroll);
    document.addEventListener('mousedown', mouseDownHandler);
})

window.addEventListener("load", function(event) {
    if(document.querySelector('.menu-item-active')){
        const element = document.querySelector('.main-img-tabs');
        const localStorageScroll = localStorage.getItem('scroll');
        if(localStorageScroll) element.scrollLeft = JSON.parse(localStorageScroll);
    }
});


