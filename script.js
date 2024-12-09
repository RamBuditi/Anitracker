const searchBox = document.getElementById('search-box');
const searchButton = document.getElementById('search-button');
const searchResultsList = document.getElementById('search-results-list');
const myAnimeList = document.getElementById('my-anime-list');

let myAnimeData = []; // Array to store the user's anime list

// Load anime data from local storage or initialize an empty array
if (localStorage.getItem('myAnimeData')) {
    myAnimeData = JSON.parse(localStorage.getItem('myAnimeData'));
    displayMyAnimeList();
}

// Function to fetch anime data from Jikan API
async function searchAnime(query) {
    const response = await fetch(`https://api.jikan.moe/v4/anime?q=${query}`);
    const data = await response.json();
    return data.data;
}

// Function to display search results
function displaySearchResults(animeData) {
    searchResultsList.innerHTML = ''; // Clear previous results

    animeData.forEach(anime => {
        const animeCard = document.createElement('div');
        animeCard.classList.add('anime-card');

        const animeImage = document.createElement('img');
        animeImage.src = anime.images.jpg.image_url;
        animeImage.alt = anime.title;

        const animeTitle = document.createElement('div');
        animeTitle.classList.add('anime-title');
        animeTitle.textContent = anime.title;

        const addButton = document.createElement('button');
        addButton.classList.add('add-button');
        addButton.textContent = 'Add to List';

        addButton.addEventListener('click', () => {
            addAnimeToMyList(anime);
        });

        animeCard.appendChild(animeImage);
        animeCard.appendChild(animeTitle);
        animeCard.appendChild(addButton);
        searchResultsList.appendChild(animeCard);
    });
}

// Function to add anime to user's list
function addAnimeToMyList(anime) {
    // Check if anime already exists in the list
    const isAnimeInList = myAnimeData.some(item => item.mal_id === anime.mal_id);
    if (!isAnimeInList) {
        myAnimeData.push(anime);
        localStorage.setItem('myAnimeData', JSON.stringify(myAnimeData));
        displayMyAnimeList();
    }
}

// Function to display user's anime list
function displayMyAnimeList() {
    myAnimeList.innerHTML = '';

    myAnimeData.forEach(anime => {
        const animeCard = document.createElement('div');
        animeCard.classList.add('anime-card');

        const animeImage = document.createElement('img');
        animeImage.src = anime.images.jpg.image_url;
        animeImage.alt = anime.title;

        const animeTitle = document.createElement('div');
        animeTitle.classList.add('anime-title');
        animeTitle.textContent = anime.title;

        const removeButton = document.createElement('button');
        removeButton.classList.add('remove-button');
        removeButton.textContent = 'Remove';

        removeButton.addEventListener('click', () => {
            removeAnimeFromMyList(anime);
        });

        animeCard.appendChild(animeImage);
        animeCard.appendChild(animeTitle);
        animeCard.appendChild(removeButton);
        myAnimeList.appendChild(animeCard);
    });
}

// Function to remove anime from user's list
function removeAnimeFromMyList(anime) {
    myAnimeData = myAnimeData.filter(item => item.mal_id !== anime.mal_id);
    localStorage.setItem('myAnimeData', JSON.stringify(myAnimeData));
    displayMyAnimeList();
}

// Event listener for search button
searchButton.addEventListener('click', async () => {
    const searchTerm = searchBox.value;
    if (searchTerm) {
        const animeData = await searchAnime(searchTerm);
        displaySearchResults(animeData);
    }
});

// Function to show/hide sections based on search results
function toggleSections() {
    const hasSearchResults = searchResultsList.children.length > 0;
    const hasMyAnimeList = myAnimeList.children.length > 0;

    document.getElementById('search-results').style.display = hasSearchResults ? 'block' : 'none';
    document.getElementById('my-list').style.display = hasMyAnimeList ? 'block' : 'none';
}

// Event listeners for search and my anime list
searchButton.addEventListener('click', async () => {
    const searchTerm = searchBox.value;
    if (searchTerm) {
        const animeData = await searchAnime(searchTerm);
        displaySearchResults(animeData);
        toggleSections();
    }
});

myAnimeList.addEventListener('DOMSubtreeModified', toggleSections);

// Initial display on page load
toggleSections();