/** @odoo-module **/

import { Interaction } from '@web/public/interaction';
import { registry } from '@web/core/registry';

// Native Odoo owns the banner carousel, navigation, cart, checkout and
// newsletter. This interaction only scrolls the homepage product shelf.
export class SuziProductShelf extends Interaction {
    static selector = '.sz-products-section';
    dynamicContent = {
        '[data-sz-prev]': { 't-on-click': () => this.scroll(-1) },
        '[data-sz-next]': { 't-on-click': () => this.scroll(1) },
    };

    scroll(direction) {
        const shelf = this.el.querySelector('[data-sz-carousel]');
        if (!shelf) return;
        const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
        shelf.scrollBy({
            left: direction * Math.max(250, shelf.clientWidth * 0.8),
            behavior: reducedMotion ? 'auto' : 'smooth',
        });
    }
}

registry.category('public.interactions').add('suzi.product_shelf', SuziProductShelf);
