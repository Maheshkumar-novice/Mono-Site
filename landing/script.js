/**
 * Portfolio Site - GitHub Integration
 * Fetches curated repositories from GitHub API
 */

const GITHUB_USERNAME = 'Maheshkumar-novice';
const GITHUB_API_URL = `https://api.github.com/users/${GITHUB_USERNAME}/repos`;

// Curated list of projects to display (repo names)
const CURATED_PROJECTS = [
    'Mono-Site',
    'Med-Reminder-Bot',
    'Chess',
    'AstroMath',
    'Advent-Of-Code-Solutions',
    'Connect-Four',
    'Mastermind',
    'TIL'
];

// External repos (from other orgs) - handled separately
const EXTERNAL_PROJECTS = [
    {
        name: 'code-jam-24-luminous-lightyears',
        owner: 'krishnabhat3383',
        description: 'Code Jam 2024 Entry for the team Luminous Lightyears',
        language: 'Python',
        stars: 3
    }
];

/**
 * Fetch repositories from GitHub API
 */
async function fetchRepositories() {
    try {
        const response = await fetch(`${GITHUB_API_URL}?per_page=100&sort=updated`);

        if (!response.ok) {
            throw new Error(`GitHub API error: ${response.status}`);
        }

        const repos = await response.json();
        return repos;
    } catch (error) {
        console.error('Failed to fetch repositories:', error);
        return null;
    }
}

/**
 * Filter repositories to only include curated projects
 */
function filterCuratedProjects(repos) {
    const curatedRepos = repos.filter(repo =>
        CURATED_PROJECTS.includes(repo.name)
    );

    // Sort by the order in CURATED_PROJECTS array
    curatedRepos.sort((a, b) => {
        return CURATED_PROJECTS.indexOf(a.name) - CURATED_PROJECTS.indexOf(b.name);
    });

    return curatedRepos;
}

/**
 * Render projects section
 */
function renderProjects(projects) {
    const list = document.getElementById('projects-list');

    if (!projects || projects.length === 0) {
        list.innerHTML = '<li class="loading-placeholder">Unable to load projects</li>';
        return;
    }

    // Combine curated repos with external projects
    const allProjects = [
        ...projects.map(project => ({
            name: project.name,
            description: project.description || 'No description',
            url: project.html_url,
            language: project.language,
            stars: project.stargazers_count
        })),
        ...EXTERNAL_PROJECTS.map(project => ({
            name: project.name,
            description: project.description,
            url: `https://github.com/${project.owner}/${project.name}`,
            language: project.language,
            stars: project.stars
        }))
    ];

    list.innerHTML = allProjects
        .map((project, index) => `
            <li class="project-item stagger-item" style="animation-delay: ${index * 80}ms">
                <a href="${project.url}" target="_blank" rel="noopener noreferrer" class="project-link">
                    <div class="project-info">
                        <h3 class="project-name">${project.name}</h3>
                        <p class="project-description">${project.description}</p>
                    </div>
                    <div class="project-meta">
                        ${project.language ? `<span class="project-language">${project.language}</span>` : ''}
                        ${project.stars > 0 ? `
                            <span class="project-stars">
                                <svg viewBox="0 0 16 16" fill="currentColor">
                                    <path d="M8 .25a.75.75 0 01.673.418l1.882 3.815 4.21.612a.75.75 0 01.416 1.279l-3.046 2.97.719 4.192a.75.75 0 01-1.088.791L8 12.347l-3.766 1.98a.75.75 0 01-1.088-.79l.72-4.194L.818 6.374a.75.75 0 01.416-1.28l4.21-.611L7.327.668A.75.75 0 018 .25z"/>
                                </svg>
                                ${project.stars}
                            </span>
                        ` : ''}
                        <span class="project-arrow">→</span>
                    </div>
                </a>
            </li>
        `)
        .join('');
}

/**
 * Fallback data in case API fails
 */
function useFallbackData() {
    const fallbackProjects = [
        {
            name: 'Mono-Site',
            description: 'Monorepo for maheshkumar.blog',
            url: 'https://github.com/Maheshkumar-novice/Mono-Site',
            language: 'Python',
            stars: 0
        },
        {
            name: 'Med-Reminder-Bot',
            description: 'Medicine Reminder Bot',
            url: 'https://github.com/Maheshkumar-novice/Med-Reminder-Bot',
            language: 'Python',
            stars: 0
        },
        {
            name: 'Chess',
            description: 'A command line game written in Ruby',
            url: 'https://github.com/Maheshkumar-novice/Chess',
            language: 'Ruby',
            stars: 2
        },
        {
            name: 'AstroMath',
            description: 'Math Game for Kids',
            url: 'https://github.com/Maheshkumar-novice/AstroMath',
            language: 'JavaScript',
            stars: 3
        },
        {
            name: 'Advent-Of-Code-Solutions',
            description: 'Advent of Code solutions',
            url: 'https://github.com/Maheshkumar-novice/Advent-Of-Code-Solutions',
            language: 'Python',
            stars: 0
        },
        {
            name: 'Connect-Four',
            description: 'A command line game written in Ruby (Test Driven Development)',
            url: 'https://github.com/Maheshkumar-novice/Connect-Four',
            language: 'Ruby',
            stars: 0
        },
        {
            name: 'Mastermind',
            description: 'A command line game written in Ruby',
            url: 'https://github.com/Maheshkumar-novice/Mastermind',
            language: 'Ruby',
            stars: 1
        },
        {
            name: 'TIL',
            description: 'Today I Learned - Daily learnings documented',
            url: 'https://github.com/Maheshkumar-novice/TIL',
            language: 'Shell',
            stars: 0
        }
    ];

    renderProjects(fallbackProjects.map(p => ({
        name: p.name,
        description: p.description,
        html_url: p.url,
        language: p.language,
        stargazers_count: p.stars
    })));
}

/**
 * Initialize the page
 */
async function init() {
    const repos = await fetchRepositories();

    if (repos) {
        const projects = filterCuratedProjects(repos);
        renderProjects(projects);
    } else {
        // Use fallback data if API fails
        useFallbackData();
    }
}

// Run when DOM is ready
document.addEventListener('DOMContentLoaded', init);
