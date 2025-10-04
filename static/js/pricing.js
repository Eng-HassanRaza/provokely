(function(){
	const toggle = document.getElementById('billingToggle');
	if(!toggle) return;
	const priceEls = document.querySelectorAll('.pricing-card .price');
	function updatePrices(){
		priceEls.forEach(el => {
			const monthly = Number(el.dataset.monthly);
			const annual = Number(el.dataset.annual);
			const currency = el.dataset.currency || '£' || '$';
			const val = toggle.checked ? annual : monthly;
			el.animate([{opacity:1},{opacity:0},{opacity:1}], { duration:250 });
			el.textContent = `${currency}${val}`;
		});
	}
	toggle.addEventListener('change', updatePrices);
	updatePrices();

	// Attach plan to checkout redirect (prep for Stripe)
	document.querySelectorAll('#pricing a.btn').forEach(btn => {
		btn.addEventListener('click', (e) => {
			// could capture selected plan here if needed
		});
	});
})(); 