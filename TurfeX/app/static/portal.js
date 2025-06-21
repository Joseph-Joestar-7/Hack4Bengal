function handlePlayerLogin() {
  const button = event.target;
  button.innerHTML = 'Loading...';
  button.disabled = true;
  
  // Add pulse animation
  button.classList.add('pulse');
  
  setTimeout(() => {
    alert('Redirecting to Player Login Portal...');
    button.innerHTML = 'Get Started';
    button.disabled = false;
    button.classList.remove('pulse');
    
    // Here you would typically redirect to the player login page
    // window.location.href = '/player-login';
  }, 1500);
}

function handleTurfOwnerLogin() {
  const button = event.target;
  button.innerHTML = 'Loading...';
  button.disabled = true;
  
  // Add pulse animation
  button.classList.add('pulse');
  
  setTimeout(() => {
    alert('Redirecting to Turf Owner Dashboard...');
    button.innerHTML = 'Get Started';
    button.disabled = false;
    button.classList.remove('pulse');
    
    // Here you would typically redirect to the turf owner login page
    // window.location.href = '/turf-owner-login';
  }, 1500);
}

// Add some interactive effects
document.addEventListener('DOMContentLoaded', function() {
  const sections = document.querySelectorAll('.section');
  
  sections.forEach(section => {
    section.addEventListener('mouseenter', function() {
      this.style.transform = 'scale(1.02)';
      this.style.transition = 'transform 0.3s ease';
    });
    
    section.addEventListener('mouseleave', function() {
      this.style.transform = 'scale(1)';
    });
  });
});
