
// TurfBook Dashboard JavaScript

// Theme Management
class ThemeManager {
    constructor() {
        this.init();
    }

    init() {
        // Check for saved theme preference or default to light mode
        const savedTheme = localStorage.getItem('theme');
        const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
        
        if (savedTheme === 'dark' || (!savedTheme && prefersDark)) {
            this.setDarkMode(true);
        } else {
            this.setDarkMode(false);
        }

        // Add event listener for theme toggle
        const themeToggle = document.getElementById('theme-toggle');
        if (themeToggle) {
            themeToggle.addEventListener('click', () => this.toggleTheme());
        }
    }

    setDarkMode(isDark) {
        if (isDark) {
            document.documentElement.classList.add('dark');
            localStorage.setItem('theme', 'dark');
        } else {
            document.documentElement.classList.remove('dark');
            localStorage.setItem('theme', 'light');
        }
    }

    toggleTheme() {
        const isDark = document.documentElement.classList.contains('dark');
        this.setDarkMode(!isDark);
    }
}

// Map Management
class MapManager {
    constructor() {
        this.map = null;
        this.init();
    }

    init() {
        // Initialize Leaflet map
        if (window.L && document.getElementById('map')) {
            this.map = L.map('map', {
                zoomControl: false,
                attributionControl: false
            }).setView([51.505, -0.09], 13);

            L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(this.map);

            // Add sample markers
            const locations = [
                { lat: 51.5, lng: -0.09, name: 'Green Valley Sports' },
                { lat: 51.51, lng: -0.1, name: 'Stadium Pro Arena' },
                { lat: 51.49, lng: -0.08, name: 'Riverside Fields' },
                { lat: 51.52, lng: -0.11, name: 'Mountain View Sports' }
            ];

            locations.forEach(location => {
                L.marker([location.lat, location.lng])
                    .addTo(this.map)
                    .bindPopup(`<b>${location.name}</b><br>Click to view details`);
            });
        }
    }
}

// Turf Data Management
class TurfManager {
    constructor() {
        this.turfData = [
            {
                id: 1,
                name: "Green Valley Sports",
                rating: 4.8,
                image: "https://wallpaperaccess.com/full/1728937.jpg",
                price: "$25/hr",
                available: true
            },
            {
                id: 2,
                name: "Stadium Pro Arena",
                rating: 4.5,
                image: "https://wallpapers.com/images/hd/yankee-stadium-lush-green-baseball-field-7elad7ok4knhv594.jpg",
                price: "$30/hr",
                available: false
            },
            {
                id: 3,
                name: "Riverside Fields",
                rating: 4.9,
                image: "https://wallpaperaccess.com/full/1925295.jpg",
                price: "$22/hr",
                available: true
            },
            {
                id: 4,
                name: "Mountain View Sports",
                rating: 4.3,
                image: "https://images.pexels.com/photos/592077/pexels-photo-592077.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=2",
                price: "$28/hr",
                available: true
            },
            {
                id: 5,
                name: "Elite Training Ground",
                rating: 4.7,
                image: "https://i.pinimg.com/736x/3c/f0/27/3cf027200a07c0da6fcfa75b131aef7d--playgrounds-basketball.jpg",
                price: "$35/hr",
                available: true
            },
            {
                id: 6,
                name: "Urban Sports Complex",
                rating: 4.4,
                image: "https://images.pexels.com/photos/19210728/pexels-photo-19210728/free-photo-of-gorsa-bridge-en-norvege-vue-de-drone-chute-d-eau-montagne-pont.jpeg?auto=compress&cs=tinysrgb&w=600",
                price: "$26/hr",
                available: false
            }
        ];
        this.init();
    }

    init() {
        this.renderFeaturedTurfs();
        this.renderAllTurfs();
    }

    createStarRating(rating) {
        const fullStars = Math.floor(rating);
        const hasHalfStar = rating % 1 !== 0;
        let starsHTML = '';

        for (let i = 0; i < fullStars; i++) {
            starsHTML += '<span class="star">★</span>';
        }

        if (hasHalfStar) {
            starsHTML += '<span class="star">☆</span>';
        }

        const emptyStars = 5 - Math.ceil(rating);
        for (let i = 0; i < emptyStars; i++) {
            starsHTML += '<span class="star empty">☆</span>';
        }

        return starsHTML;
    }

    createTurfCard(turf, isSmall = false) {
        const availabilityClass = turf.available 
            ? 'bg-green-500/80 text-white' 
            : 'bg-red-500/80 text-white';
        
        const availabilityText = turf.available ? '✅ Available' : '🔴 Booked';
        const imageHeight = isSmall ? 'h-32' : 'h-48';

        return `
            <div class="turf-card glass-card rounded-3xl overflow-hidden hover:scale-105 transition-all duration-500 group cursor-pointer shadow-xl">
                <div class="relative">
                    <img 
                        src="${turf.image}" 
                        alt="${turf.name}"
                        class="w-full ${imageHeight} object-cover group-hover:scale-110 transition-transform duration-500"
                    />
                    <div class="absolute inset-0 bg-gradient-to-t from-black/50 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
                    <div class="absolute top-3 right-3">
                        <div class="availability-badge px-3 py-1 rounded-full text-xs font-bold ${availabilityClass}">
                            ${availabilityText}
                        </div>
                    </div>
                    <div class="absolute bottom-3 left-3 right-3 opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                        <button class="book-btn w-full bg-emerald-500/90 text-white py-2 rounded-xl font-semibold backdrop-blur-sm hover:bg-emerald-400 transition-colors">
                            Book Now
                        </button>
                    </div>
                </div>
                
                <div class="p-4">
                    <h3 class="font-bold text-gray-800 dark:text-white mb-2 group-hover:text-emerald-600 dark:group-hover:text-emerald-400 transition-colors">
                        ${turf.name}
                    </h3>
                    <div class="flex items-center justify-between">
                        <div class="flex items-center">
                            <div class="star-rating text-sm">
                                ${this.createStarRating(turf.rating)}
                            </div>
                            <span class="text-gray-600 dark:text-gray-400 text-sm ml-2">${turf.rating}</span>
                        </div>
                        <div class="text-emerald-600 dark:text-emerald-400 font-bold text-lg">
                            ${turf.price}
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    renderFeaturedTurfs() {
        const container = document.getElementById('featured-turfs');
        if (container) {
            const featuredTurfs = this.turfData.slice(0, 4);
            container.innerHTML = featuredTurfs
                .map(turf => this.createTurfCard(turf, true))
                .join('');
        }
    }

    renderAllTurfs() {
        const container = document.getElementById('all-turfs');
        if (container) {
            container.innerHTML = this.turfData
                .map(turf => this.createTurfCard(turf, false))
                .join('');
        }
    }
}

// Animation and Effects Manager
class AnimationManager {
    constructor() {
        this.init();
    }

    init() {
        this.setupScrollEffects();
        this.setupScrollAnimations();
    }

    setupScrollEffects() {
        const navbar = document.getElementById('navbar');
        const floatingShapes = document.querySelectorAll('.floating-shape');
        
        const handleScroll = () => {
            const scrolled = window.pageYOffset;
            
            // Navbar blur effect
            if (scrolled > 50) {
                navbar.classList.add('scrolled');
            } else {
                navbar.classList.remove('scrolled');
            }
            
            // Floating shapes parallax (only move the 3D elements, not the entire background)
            floatingShapes.forEach((shape, index) => {
                const speed = 0.5 + (index * 0.1); // Different speeds for each shape
                const yPos = scrolled * speed;
                shape.style.transform = `translateY(${yPos}px) ${shape.style.transform.includes('perspective') ? shape.style.transform.split('translateY')[1]?.split(')')[1] || '' : ''}`;
            });
        };

        window.addEventListener('scroll', handleScroll);
    }

    setupScrollAnimations() {
        // Intersection Observer for scroll animations
        const observerOptions = {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        };

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.style.animationPlayState = 'running';
                }
            });
        }, observerOptions);

        // Observe all turf cards
        setTimeout(() => {
            const turfCards = document.querySelectorAll('.turf-card');
            turfCards.forEach(card => {
                card.style.animationPlayState = 'paused';
                observer.observe(card);
            });
        }, 100);
    }
}

// Search and Filter Manager
class SearchManager {
    constructor(turfManager) {
        this.turfManager = turfManager;
        this.init();
    }

    init() {
        const searchInput = document.querySelector('input[placeholder*="Search"]');
        if (searchInput) {
            searchInput.addEventListener('input', (e) => {
                this.handleSearch(e.target.value);
            });
        }

        // Add event listeners for action buttons
        const liveMatchesBtn = document.querySelector('button:contains("🔴 Live Matches")');
        const createMatchBtn = document.querySelector('button:contains("➕ Create Match")');

        // Note: For full functionality, you would implement these features
        // For now, they can show alerts or redirect to appropriate pages
    }

    handleSearch(query) {
        // Filter turfs based on search query
        const filteredTurfs = this.turfManager.turfData.filter(turf =>
            turf.name.toLowerCase().includes(query.toLowerCase())
        );

        // Update the display (you can extend this functionality)
        console.log('Searching for:', query);
        console.log('Filtered results:', filteredTurfs);
    }
}

// Main Application Class
class TurfBookApp {
    constructor() {
        this.themeManager = null;
        this.mapManager = null;
        this.turfManager = null;
        this.animationManager = null;
        this.searchManager = null;
        this.init();
    }

    init() {
        // Wait for DOM to be ready
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.initializeApp());
        } else {
            this.initializeApp();
        }
    }

    initializeApp() {
        try {
            // Initialize all managers
            this.themeManager = new ThemeManager();
            this.mapManager = new MapManager();
            this.turfManager = new TurfManager();
            this.animationManager = new AnimationManager();
            this.searchManager = new SearchManager(this.turfManager);

            console.log('TurfBook Dashboard initialized successfully');
        } catch (error) {
            console.error('Error initializing TurfBook Dashboard:', error);
        }
    }
}

// Initialize the application
const app = new TurfBookApp();

// Utility functions for potential Flask integration
window.TurfBookAPI = {
    // Function to update turf data from Flask backend
    updateTurfData: function(newData) {
        if (app.turfManager) {
            app.turfManager.turfData = newData;
            app.turfManager.renderFeaturedTurfs();
            app.turfManager.renderAllTurfs();
        }
    },

    // Function to get current theme
    getCurrentTheme: function() {
        return document.documentElement.classList.contains('dark') ? 'dark' : 'light';
    },

    // Function to handle booking (to be connected with Flask)
    bookTurf: function(turfId) {
        console.log('Booking turf with ID:', turfId);
        // This can be connected to your Flask backend
        // fetch('/api/book-turf', { method: 'POST', body: JSON.stringify({turfId}) })
    },

    // Function to search turfs
    searchTurfs: function(query) {
        if (app.searchManager) {
            app.searchManager.handleSearch(query);
        }
    }
};


class CreateMatchManager {
            constructor() {
                this.init();
            }

            init() {
                const generateBtn = document.getElementById('generate-code-btn');
                const copyBtn = document.getElementById('copy-code-btn');

                if (generateBtn) {
                    generateBtn.addEventListener('click', () => this.generateTeamCode());
                }

                if (copyBtn) {
                    copyBtn.addEventListener('click', () => this.copyTeamCode());
                }
            }

            generateTeamCode() {
                const teamName = document.getElementById('team-name').value;
                const gameType = document.getElementById('game-type').value;

                if (!teamName || !gameType) {
                    alert('Please fill in team name and game type first!');
                    return;
                }

                // Generate a random 6-character code
                const code = Math.random().toString(36).substring(2, 8).toUpperCase();
                
                document.getElementById('team-code').value = code;
                document.getElementById('team-code-section').classList.remove('hidden');

                // Update button text
                document.getElementById('generate-code-btn').innerHTML = '🔄 Generate New Code';
            }

            copyTeamCode() {
                const codeInput = document.getElementById('team-code');
                codeInput.select();
                document.execCommand('copy');

                // Show feedback
                const copyBtn = document.getElementById('copy-code-btn');
                const originalText = copyBtn.innerHTML;
                copyBtn.innerHTML = '✅ Copied!';
                
                setTimeout(() => {
                    copyBtn.innerHTML = originalText;
                }, 2000);
            }
        }

// Main Application Class
        class LiveMatchesApp {
            constructor() {
                this.themeManager = null;
                this.animationManager = null;
                this.init();
            }

            init() {
                if (document.readyState === 'loading') {
                    document.addEventListener('DOMContentLoaded', () => this.initializeApp());
                } else {
                    this.initializeApp();
                }
            }

            initializeApp() {
                try {
                    this.themeManager = new ThemeManager();
                    this.animationManager = new AnimationManager();

                    // Add click handlers for join match buttons
                    const joinButtons = document.querySelectorAll('.match-card button');
                    joinButtons.forEach(button => {
                        button.addEventListener('click', this.handleJoinMatch);
                    });

                    console.log('Live Matches page initialized successfully');
                } catch (error) {
                    console.error('Error initializing Live Matches page:', error);
                }
            }

            handleJoinMatch(event) {
                const button = event.target;
                const card = button.closest('.match-card');
                const teamName = card.querySelector('h3').textContent;
                
                // Add visual feedback
                button.textContent = '✅ Joining...';
                button.disabled = true;
                
                // Simulate joining process
                setTimeout(() => {
                    button.textContent = '🎉 Joined!';
                    button.classList.remove('bg-gradient-to-r', 'from-emerald-500', 'to-teal-500');
                    button.classList.add('bg-green-500');
                    
                    // Show success message
                    console.log(`Successfully joined ${teamName}!`);
                }, 1000);
            }
        }

// Animation delay for content cards
        const contentCards = document.querySelectorAll('.content-card');
        contentCards.forEach((card, index) => {
            card.style.animationDelay = `${index * 200}ms`;
        });

        // Review form functionality
        const addReviewBtn = document.getElementById('add-review-btn');
        const reviewForm = document.getElementById('review-form');
        const cancelReviewBtn = document.getElementById('cancel-review');
        const submitReviewBtn = document.getElementById('submit-review');
        const reviewText = document.getElementById('review-text');
        const reviewsList = document.getElementById('reviews-list');
        const starRatings = document.querySelectorAll('.star-rating');

        let selectedRating = 0;

        // Show/hide review form
        addReviewBtn.addEventListener('click', () => {
            reviewForm.classList.remove('hidden');
            addReviewBtn.style.display = 'none';
        });

        cancelReviewBtn.addEventListener('click', () => {
            reviewForm.classList.add('hidden');
            addReviewBtn.style.display = 'flex';
            resetReviewForm();
        });

        // Star rating functionality
        starRatings.forEach(star => {
            star.addEventListener('click', () => {
                selectedRating = parseInt(star.dataset.rating);
                updateStarDisplay();
            });

            star.addEventListener('mouseenter', () => {
                const rating = parseInt(star.dataset.rating);
                highlightStars(rating);
            });
        });

        document.querySelector('.star-rating').parentElement.addEventListener('mouseleave', () => {
            updateStarDisplay();
        });

        function highlightStars(rating) {
            starRatings.forEach((star, index) => {
                if (index < rating) {
                    star.classList.add('text-yellow-400');
                    star.classList.remove('text-gray-300');
                } else {
                    star.classList.add('text-gray-300');
                    star.classList.remove('text-yellow-400');
                }
            });
        }

        function updateStarDisplay() {
            highlightStars(selectedRating);
        }

        function resetReviewForm() {
            selectedRating = 0;
            reviewText.value = '';
            updateStarDisplay();
        }

        // Submit review
        submitReviewBtn.addEventListener('click', () => {
            if (selectedRating === 0 || reviewText.value.trim() === '') {
                alert('Please provide a rating and review text.');
                return;
            }

            // Create new review element
            const newReview = document.createElement('div');
            newReview.className = 'bg-white/10 dark:bg-gray-800/20 rounded-2xl p-6 backdrop-blur-sm border border-white/20 dark:border-gray-700/20 hover:bg-white/20 dark:hover:bg-gray-800/30 transition-all duration-300';
            
            const stars = '★'.repeat(selectedRating) + '☆'.repeat(5 - selectedRating);
            
            newReview.innerHTML = `
                <div class="flex items-start justify-between mb-3">
                    <div>
                        <h4 class="font-semibold text-gray-800 dark:text-gray-200">Anonymous User</h4>
                        <div class="flex text-yellow-400 text-lg">${stars}</div>
                    </div>
                    <span class="text-sm text-gray-600 dark:text-gray-400">Just now</span>
                </div>
                <p class="text-gray-700 dark:text-gray-300">${reviewText.value.trim()}</p>
            `;

            // Add to reviews list at the top
            reviewsList.insertBefore(newReview, reviewsList.firstChild);

            // Hide form and reset
            reviewForm.classList.add('hidden');
            addReviewBtn.style.display = 'flex';
            resetReviewForm();

            // Show success message
            const successMsg = document.createElement('div');
            successMsg.className = 'fixed top-24 right-6 bg-green-500 text-white px-6 py-3 rounded-lg shadow-lg z-50';
            successMsg.textContent = 'Review submitted successfully!';
            document.body.appendChild(successMsg);

            setTimeout(() => {
                successMsg.remove();
            }, 3000);
        });