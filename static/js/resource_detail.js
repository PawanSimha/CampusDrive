/**
 * Resource Detail page — Star rating interaction logic
 * Used by resource_detail.html
 */

function updateStars(container, count) {
    const stars = container.querySelectorAll('.material-symbols-rounded');
    stars.forEach((s, i) => {
        if (i < count) {
            s.classList.remove('text-slate-200');
            s.classList.add('text-primary-600');
        } else {
            s.classList.add('text-slate-200');
            s.classList.remove('text-primary-600');
        }
    });
}

document.addEventListener('DOMContentLoaded', () => {
    const starContainer = document.querySelector('.star-container');
    if (!starContainer) return;

    const radios = document.querySelectorAll('input[name="rating"]');
    const stars = document.querySelectorAll('.star-rating-trigger');

    // Initialize stars on load if rating exists
    const checked = document.querySelector('input[name="rating"]:checked');
    if (checked) {
        updateStars(starContainer, parseInt(checked.value));
    }

    stars.forEach(star => {
        star.addEventListener('click', function() {
            const index = parseInt(this.getAttribute('data-star-index'));
            const radio = this.previousElementSibling;
            radio.checked = true;
            updateStars(starContainer, index);
        });

        star.addEventListener('mouseover', function() {
            const index = parseInt(this.getAttribute('data-star-index'));
            stars.forEach((s, i) => {
                if (i < index) {
                    s.classList.remove('text-slate-200');
                    s.classList.add('text-primary-600');
                } else {
                    s.classList.add('text-slate-200');
                    s.classList.remove('text-primary-600');
                }
            });
        });
    });

    starContainer.addEventListener('mouseleave', () => {
        const checked = document.querySelector('input[name="rating"]:checked');
        const val = checked ? parseInt(checked.value) : 0;
        updateStars(starContainer, val);
    });
});

