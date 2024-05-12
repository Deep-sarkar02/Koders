// Array of entity names for iteration
const entities = [
  'timestamp', 'average-sales-revenue', 'baby-product', 'baked-product', 'baking-product',
  'beverage-product', 'canned-product', 'cheese-product', 'cleaning-product', 'condiment-and-sauces',
  'category-dairy', 'category-frozen', 'category-fruits', 'kitchen', 'meat', 'medicine',
  'packaged-food', 'personal-care', 'pets', 'refrigerated-items', 'seafood', 'snacks',
  'spice-and-herb', 'vegetables', 'quantity', 'market-share'
];

// Add event listeners and display logic for each entity
entities.forEach(entity => {
  const yesRadio = document.getElementById(`${entity}-yes`);
  const noRadio = document.getElementById(`${entity}-no`);
  yesRadio.addEventListener('change', displayImage);
  noRadio.addEventListener('change', displayImage);
});

function displayImage() {
  // Clear any existing images
  imageContainer.innerHTML = '';

  // Check for each entity if "Yes" is selected and display the corresponding image
  if (timestampYesRadio.checked && averageSalesRevenueYesRadio.checked) {
    displayLocalImage('timestamp-average-sales-revenue.jpg');
  }

  entities.forEach(entity => {
    const yesRadio = document.getElementById(`${entity}-yes`);
    if (yesRadio.checked) {
      displayLocalImage(`${entity}.jpg`); // Display locally available image
    }
  });
}

function displayLocalImage(imagePath) {
  const image = document.createElement('img');
  image.src = imagePath;
  imageContainer.appendChild(image);
}