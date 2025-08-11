const imageContainer = document.getElementById('image-container');
const currentImage = document.getElementById('current-image');
const prevButton = document.getElementById('prev-button');
const nextButton = document.getElementById('next-button');
const imageTitle = document.getElementById('image-title');
const imageDescription = document.getElementById('image-description');

// 假设图片文件在当前目录下
const imageFiles = [
    "20240714-223921.jpeg",
    "20240714-223928.jpeg",
    "20240708162241_1.jpg",
    "20240708164608_1.jpg",
    "20240708184737_1.jpg",
    "20240709115119_1.jpg",
    "20240709120639_1.jpg",
    "20240710183759_1.jpg",
    "20240710183807_1.jpg",
    "20240710183818_1.jpg",
    "20240710183824_1.jpg"
];

let currentImageIndex = 0;

function displayImage(index) {
    currentImage.src = "/ProjectKOTeam/src/cliProject/localCliLLM/image_view/" + imageFiles[index];
    imageTitle.textContent = `图片 ${index + 1}`;
    imageDescription.textContent = `这是一张本地图片。`;
}

function previousImage() {
    currentImageIndex = (currentImageIndex - 1 + imageFiles.length) % imageFiles.length;
    displayImage(currentImageIndex);
}

function nextImage() {
    currentImageIndex = (currentImageIndex + 1) % imageFiles.length;
    displayImage(currentImageIndex);
}

// 初始化时显示第一张图片
displayImage(currentImageIndex);

// 点击事件处理
prevButton.addEventListener('click', previousImage);
nextButton.addEventListener('click', nextImage);

// 动画效果
currentImage.addEventListener('mouseover', () => {
    currentImage.classList.add('zoom');
});

currentImage.addEventListener('mouseout', () => {
    currentImage.classList.remove('zoom');
});
