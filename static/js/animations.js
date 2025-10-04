// Trust badge and multi-counter animation
(function(){
	function animateCount(el){
		let started = false;
		const target = Number(el.dataset.count || 0);
		const io = new IntersectionObserver((entries) => {
			if(entries.some(e => e.isIntersecting)){
				if(started) return; started = true;
				const duration = 1200;
				const start = performance.now();
				function tick(now){
					const p = Math.min(1, (now - start)/duration);
					el.textContent = Math.floor(p * target).toString();
					if(p < 1) requestAnimationFrame(tick);
				}
				requestAnimationFrame(tick);
				io.disconnect();
			}
		},{ threshold: 0.6 });
		io.observe(el);
	}
	// single legacy id support
	const legacy = document.getElementById('trust-counter');
	if(legacy) animateCount(legacy);
	// new counters
	document.querySelectorAll('.count').forEach(animateCount);
})(); 