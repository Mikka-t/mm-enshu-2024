const ANIMATION_TIME = 250;
    const OFFSET_TIME = 5;

    document.addEventListener('DOMContentLoaded', function () {

        const accordions = document.querySelectorAll('.details');
        accordions.forEach((accordion) => {
            const title = accordion.querySelector('.summary');
            title.addEventListener('click', (e) => {
                e.preventDefault();
                if (!accordion.open) {
                    accordion.open = true;
                    setTimeout(() => {
                        accordion.classList.add('is-opened');
                    }, OFFSET_TIME);
                    //
                } else if (accordion.open) {
                    accordion.classList.remove('is-opened');
                    setTimeout(() => {
                        accordion.open = false;
                    }, ANIMATION_TIME + OFFSET_TIME);
                }
            });


            accordion.addEventListener('toggle', () => {
                const hasOpenedClass = accordion.classList.contains('is-opened');

                if (accordion.open && !hasOpenedClass) {
                    accordion.classList.add('is-opened');
                } else if (!accordion.open && hasOpenedClass) {
                    accordion.classList.remove('is-opened');
                }
            });
        });
    });



    //以下はtableをスクロールするためのやつ
function scrollSection(direction) {
    const container = document.querySelector('.sections-wrapper');
    const scrollAmount = window.innerWidth; // Adjust this value as needed
    const currentScroll = container.scrollLeft;
    container.scrollTo({
        top: 0,
        left: currentScroll + (scrollAmount * direction),
        behavior: 'smooth'
    });
    }

