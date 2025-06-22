
// Stats Page JavaScript

// Stats Page Management
class StatsManager {
    constructor() {
        this.init();
    }

    init() {
        // Only initialize charts if we're on the stats page
        if (document.getElementById('matchesChart')) {
            this.initializeCharts();
        }

        // Mobile Menu Toggle
        this.initializeMobileMenu();

        // Theme Management
        this.initializeTheme();
    }

    initializeTheme() {
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

    initializeMobileMenu() {
        const mobileMenuButton = document.getElementById('mobile-menu-button');
        const mobileMenu = document.getElementById('mobile-menu');
        
        if (mobileMenuButton && mobileMenu) {
            mobileMenuButton.addEventListener('click', () => {
                mobileMenu.classList.toggle('hidden');
            });
        }
    }

    initializeCharts() {
        // Wait for Chart.js to load
        if (typeof Chart === 'undefined') {
            console.error('Chart.js is not loaded');
            return;
        }

        // Matches Played Over Time Chart
        const matchesCtx = document.getElementById('matchesChart');
        if (matchesCtx) {
            new Chart(matchesCtx.getContext('2d'), {
                type: 'line',
                data: {
                    labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
                    datasets: [{
                        label: 'Matches Played',
                        data: [2, 8, 5, 6, 5, 2, 5, 8, 6, 7, 6, 4],
                        borderColor: '#10B981',
                        backgroundColor: 'rgba(16, 185, 129, 0.1)',
                        tension: 0.4,
                        fill: true
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            labels: {
                                color: '#374151'
                            }
                        }
                    },
                    scales: {
                        x: {
                            ticks: {
                                color: '#6B7280'
                            },
                            grid: {
                                color: 'rgba(107, 114, 128, 0.2)'
                            }
                        },
                        y: {
                            ticks: {
                                color: '#6B7280'
                            },
                            grid: {
                                color: 'rgba(107, 114, 128, 0.2)'
                            }
                        }
                    }
                }
            });
        }

        // Game Types Distribution Chart
        const gameTypesCtx = document.getElementById('gameTypesChart');
        if (gameTypesCtx) {
            new Chart(gameTypesCtx.getContext('2d'), {
                type: 'doughnut',
                data: {
                    labels: ['Cricket', 'Football', 'Tennis'],
                    datasets: [{
                        data: [45, 32, 28],
                        backgroundColor: [
                            '#F59E0B',
                            '#EF4444',
                            '#8B5CF6'
                        ],
                        borderWidth: 0
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'bottom',
                            labels: {
                                color: '#374151',
                                padding: 20,
                                usePointStyle: true
                            }
                        }
                    }
                }
            });
        }

        // Skill Level Distribution Chart
        const skillLevelCtx = document.getElementById('skillLevelChart');
        if (skillLevelCtx) {
            // Create custom skill level mapping
            const skillLevels = ['Beginner', 'Intermediate', 'Advanced'];
            const sportSkills = {
                'Cricket': 'Advanced',
                'Football': 'Intermediate', 
                'Tennis': 'Advanced'
            };
            
            // Convert skill levels to numeric values for chart
            const skillData = Object.keys(sportSkills).map(sport => {
                const skill = sportSkills[sport];
                return skillLevels.indexOf(skill);
            });
            
            new Chart(skillLevelCtx.getContext('2d'), {
                type: 'bar',
                data: {
                    labels: ['Cricket', 'Football', 'Tennis'],
                    datasets: [{
                        label: 'Skill Level',
                        data: skillData,
                        backgroundColor: [
                            '#F59E0B',
                            '#EF4444', 
                            '#8B5CF6'
                        ],
                        borderWidth: 0,
                        borderRadius: 8
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            display: false
                        }
                    },
                    scales: {
                        x: {
                            ticks: {
                                color: '#6B7280'
                            },
                            grid: {
                                display: false
                            }
                        },
                        y: {
                            beginAtZero: true,
                            max: 2,
                            ticks: {
                                color: '#6B7280',
                                stepSize: 1,
                                callback: function(value) {
                                    return skillLevels[value] || '';
                                }
                            },
                            grid: {
                                color: 'rgba(107, 114, 128, 0.2)'
                            }
                        }
                    }
                }
            });
        }
    }
}

// Initialize the stats page when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    new StatsManager();
});

// Also initialize if DOM is already ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => new StatsManager());
} else {
    new StatsManager();
}
