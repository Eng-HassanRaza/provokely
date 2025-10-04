// AOS init
window.addEventListener('load', () => {
	if (window.AOS) {
		const prefersReduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
		AOS.init({ duration: prefersReduced ? 0 : 700, offset: 80, easing: 'ease-out-cubic', once: true, disable: prefersReduced });
	}
});

// Smooth scroll for anchor links
const headerOffset = 72; // fixed navbar height approximation
function smoothScrollTo(hash){
	const target = document.querySelector(hash);
	if(!target) return;
	const top = target.getBoundingClientRect().top + window.pageYOffset - headerOffset;
	window.scrollTo({ top, behavior:'smooth' });
}

document.addEventListener('click', (e) => {
	const link = e.target.closest('a[href^="#"]');
	if(!link) return;
	const href = link.getAttribute('href');
	if(href.length > 1){
		e.preventDefault();
		smoothScrollTo(href);
	}
});

// Active navigation via Intersection Observer
const sections = document.querySelectorAll('section[id]');
const navLinks = new Map(Array.from(document.querySelectorAll('.navbar .nav-link'))
	.filter(a => a.hash)
	.map(a => [a.hash.replace('#',''), a])
);

const observer = new IntersectionObserver((entries) => {
	entries.forEach(entry => {
		const id = entry.target.getAttribute('id');
		const link = navLinks.get(id);
		if(!link) return;
		if(entry.isIntersecting){
			link.classList.add('active');
			link.setAttribute('aria-current','true');
		}else{
			link.classList.remove('active');
			link.removeAttribute('aria-current');
		}
	});
},{ rootMargin: '-40% 0px -55% 0px', threshold: 0.01 });

sections.forEach(s => observer.observe(s));

// Scroll-to-top button
(function(){
	const btn = document.createElement('button');
	btn.className = 'btn btn-primary position-fixed';
	btn.style.cssText = 'right:16px; bottom:16px; display:none; z-index:1050;';
	btn.setAttribute('aria-label','Scroll to top');
	btn.innerHTML = '<i class="bi bi-arrow-up"></i>';
	document.body.appendChild(btn);
	btn.addEventListener('click', () => window.scrollTo({ top:0, behavior:'smooth' }));
	let visible = false;
	window.addEventListener('scroll', () => {
		const shouldShow = window.scrollY > 300;
		if(shouldShow !== visible){
			visible = shouldShow;
			btn.style.display = visible ? 'inline-flex' : 'none';
		}
	});
})();

// Navbar background on scroll and menu open
(function(){
	const nav = document.querySelector('.navbar');
	if(!nav) return;
	function onScroll(){
		nav.classList.toggle('is-scrolled', window.scrollY > 4);
	}
	window.addEventListener('scroll', onScroll, { passive:true });
	onScroll();
	// also apply when mobile menu is opened
	document.addEventListener('show.bs.collapse', (e) => {
		if(e.target && e.target.id === 'navMain') nav.classList.add('is-scrolled');
	});
	document.addEventListener('hidden.bs.collapse', (e) => {
		if(e.target && e.target.id === 'navMain') onScroll();
	});
})(); 