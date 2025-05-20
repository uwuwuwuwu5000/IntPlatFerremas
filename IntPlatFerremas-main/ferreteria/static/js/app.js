let nextBtn = document.querySelector('.next')
let prevBtn = document.querySelector('.prev')

let slider = document.querySelector('.slider')
let sliderList = slider.querySelector('.slider .list')
let thumbnail = document.querySelector('.thumbnail')
let thumbnailItems = thumbnail.querySelectorAll('.item')

thumbnail.appendChild(thumbnailItems[0])

// Funcion para next button
nextBtn.onclick = function(){
    moveSlider('next')
}

// Funcion para prev button
prevBtn.onclick = function(){
    moveSlider('prev')
}

function moveSlider(direction){
    let sliderItems = slider.querySelectorAll('.item')
    if(direction === 'next'){
        sliderList.appendChild(sliderItems[0])
        thumbnail.appendChild(thumbnailItems[0])
        slider.classList.add('next')
    }
}
document.addEventListener('DOMContentLoaded', function () {
    console.log("DOM completamente cargado.");
    
    const toggleBtn = document.querySelector('.toggle-btn');
    const links = document.querySelector('.links');

    console.log("toggleBtn:", toggleBtn);
    console.log("links:", links);

    if (toggleBtn && links) {
        toggleBtn.addEventListener('click', function () {
            links.classList.toggle('active');
        });

        document.addEventListener('click', function (event) {
            if (!links.contains(event.target) && !toggleBtn.contains(event.target)) {
                links.classList.remove('active');
            }
        });
    } else {
        console.warn("El menú de navegación o el botón no se encuentran en esta página.");
    }
});





