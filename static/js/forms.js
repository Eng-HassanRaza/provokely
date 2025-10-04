// Helpers
function getCsrfToken(){
	const el = document.querySelector('input[name="csrfmiddlewaretoken"]');
	return el ? el.value : '';
}

function isValidEmail(value){
	return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(String(value).toLowerCase());
}

async function postForm(url, data){
	const res = await fetch(url, {
		method:'POST',
		headers:{ 'X-Requested-With':'XMLHttpRequest', 'X-CSRFToken': getCsrfToken() },
		body:data
	});
	if(!res.ok) throw new Error('Network error');
	return res.json().catch(() => ({ success:true }));
}

function attachEmailValidation(input, errorEl){
	input.addEventListener('input', () => {
		const ok = isValidEmail(input.value);
		errorEl.classList.toggle('d-none', ok);
		if(!ok){ errorEl.textContent = 'Please enter a valid email address.'; }
	});
}

// Newsletter form
(function(){
	const form = document.getElementById('newsletter-form');
	if(!form) return;
	const input = document.getElementById('newsletter-email');
	const err = document.getElementById('newsletter-error');
	const ok = document.getElementById('newsletter-success');
	attachEmailValidation(input, err);
	form.addEventListener('submit', async (e) => {
		e.preventDefault();
		if(!isValidEmail(input.value)) { err.classList.remove('d-none'); return; }
		const data = new FormData(form);
		try{
			ok.classList.add('d-none'); err.classList.add('d-none');
			form.querySelector('button[type="submit"]').disabled = true;
			await postForm(form.action, data);
			ok.textContent = 'Subscribed! Check your inbox.';
			ok.classList.remove('d-none');
			form.reset();
		}catch(ex){
			err.textContent = 'Something went wrong. Please try again.';
			err.classList.remove('d-none');
		}finally{
			form.querySelector('button[type="submit"]').disabled = false;
		}
	});
})();

// Email popup modal logic
(function(){
	const modalEl = document.getElementById('emailModal');
	if(!modalEl) return;
	const form = document.getElementById('email-modal-form');
	const input = document.getElementById('email-modal-input');
	const err = document.getElementById('email-modal-error');
	const ok = document.getElementById('email-modal-success');
	attachEmailValidation(input, err);

	const storageKeySubmitted = 'provokely_modal_submitted';
	const storageKeyClosedAt = 'provokely_modal_closed_at';
	const sessionKeyShown = 'provokely_modal_shown_session';

	if(sessionStorage.getItem(sessionKeyShown) === '1') return;
	if(localStorage.getItem(storageKeySubmitted) === '1') return;
	const closedAt = Number(localStorage.getItem(storageKeyClosedAt) || 0);
	if(Date.now() - closedAt < 24*60*60*1000) return; // 24h cooldown

	const bsModal = new bootstrap.Modal(modalEl);
	let scheduled = false;
	function showModal(){
		if(scheduled) return; scheduled = true;
		bsModal.show();
		sessionStorage.setItem(sessionKeyShown,'1');
	}
	// 30s timer
	setTimeout(showModal, 30000);
	// exit intent
	document.addEventListener('mouseleave', (e) => {
		if(e.clientY <= 0) showModal();
	});

	modalEl.addEventListener('hidden.bs.modal', () => {
		localStorage.setItem(storageKeyClosedAt, String(Date.now()));
	});

	form.addEventListener('submit', async (e) => {
		e.preventDefault();
		if(!isValidEmail(input.value)) { err.classList.remove('d-none'); return; }
		const data = new FormData(form);
		try{
			ok.classList.add('d-none'); err.classList.add('d-none');
			form.querySelector('button[type="submit"]').disabled = true;
			await postForm(form.action, data);
			ok.textContent = 'Thanks! Check your inbox.';
			ok.classList.remove('d-none');
			localStorage.setItem(storageKeySubmitted,'1');
			setTimeout(() => bsModal.hide(), 1200);
		}catch(ex){
			err.textContent = 'Please try again later.';
			err.classList.remove('d-none');
		}finally{
			form.querySelector('button[type="submit"]').disabled = false;
		}
	});
})();

// Contact form
(function(){
	const form = document.getElementById('contact-form');
	if(!form) return;
	const nameInput = document.getElementById('contact-name');
	const emailInput = document.getElementById('contact-email');
	const msgInput = document.getElementById('contact-message');
	const err = document.getElementById('contact-error');
	const ok = document.getElementById('contact-success');
	attachEmailValidation(emailInput, err);
	form.addEventListener('submit', async (e) => {
		e.preventDefault();
		if(!nameInput.value.trim()){ err.textContent = 'Please enter your name.'; err.classList.remove('d-none'); return; }
		if(!isValidEmail(emailInput.value)){ err.textContent = 'Please enter a valid email address.'; err.classList.remove('d-none'); return; }
		if(!msgInput.value.trim()){ err.textContent = 'Please enter a message.'; err.classList.remove('d-none'); return; }
		const data = new FormData(form);
		try{
			ok.classList.add('d-none'); err.classList.add('d-none');
			form.querySelector('button[type="submit"]').disabled = true;
			await postForm(form.action, data);
			ok.textContent = 'Thanks! We will get back to you soon.';
			ok.classList.remove('d-none');
			form.reset();
		}catch(ex){
			err.textContent = 'Something went wrong. Please try again later.';
			err.classList.remove('d-none');
		}finally{
			form.querySelector('button[type="submit"]').disabled = false;
		}
	});
})(); 