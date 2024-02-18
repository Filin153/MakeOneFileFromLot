document.addEventListener("DOMContentLoaded", function () {
    const dropZone = document.getElementById("dropZone");
    const fileInput = document.getElementById("fileInput");
    const uploadButton = document.getElementById("uploadButton");

    let selectedFile = null;

    dropZone.addEventListener("dragover", function (e) {
        e.preventDefault();
        dropZone.classList.add("dragover");
    });

    dropZone.addEventListener("dragleave", function () {
        dropZone.classList.remove("dragover");
    });

    dropZone.addEventListener("drop", function (e) {
        e.preventDefault();
        dropZone.classList.remove("dragover");

        const file = e.dataTransfer.files[0];
        handleFile(file);
    });

    fileInput.addEventListener("change", function () {
        const file = fileInput.files[0];
        handleFile(file);
    });

    uploadButton.addEventListener("click", function () {
        if (selectedFile) {
            // Отобразить индикатор загрузки
            const loadingIndicator = document.getElementById('loadingIndicator');
            loadingIndicator.style.display = 'block';

            uploadFile(selectedFile)
                .catch(error => {
                    console.error('Ошибка при загрузке файла:', error);
                    alert('Произошла ошибка при загрузке файла.');
                })
                .finally(() => {
                    // Скрыть индикатор загрузки независимо от результата запроса
                    loadingIndicator.style.display = 'none';
                });
        } else {
            alert("Пожалуйста, выберите .zip для загрузки.");
        }
    });


    function handleFile(file) {
        if (file && file.name.endsWith(".zip")) {
            selectedFile = file;
            displayFile(file);
        } else {
            alert("Пожалуйста, выберите .zip");
        }
    }

    function displayFile(file) {
        const fileInfo = document.createElement("p");
        fileInfo.textContent = `Выбранный файл: ${file.name}`;

        // Очищаем предыдущий выбранный файл перед добавлением нового
        dropZone.innerHTML = "";

        dropZone.appendChild(fileInfo);
    }

    function uploadFile(file) {
        const formData = new FormData();
        formData.append('file', file);


    fetch('http://localhost:8000/file/load', {
        method: 'POST',
        body: formData
    })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }

            // Extract filename from the Content-Disposition header
            const contentDisposition = response.headers.get('content-disposition');
            const match = contentDisposition && contentDisposition.match(/filename=(.*)/);

            // Use the matched filename or a default if not available
            const filename = match ? match[1] : 'downloaded_file.xlsx';

            return response.blob().then(blob => ({ blob, filename }));
        })
        .then(data => {
            // Create a Blob URL for the file content
            const url = URL.createObjectURL(data.blob);

            // Create an anchor element
            const a = document.createElement('a');
            a.href = url;
            a.download = data.filename; // Use the extracted filename

            // Append the anchor element to the document body
            document.body.appendChild(a);

            // Trigger a click event on the anchor element
            a.click();

            // Remove the anchor element from the document body
            document.body.removeChild(a);

            // Revoke the Blob URL to free up resources
            URL.revokeObjectURL(url);
        })
        .catch(error => {
            const loadingIndicator = document.getElementById('loadingIndicator');
            loadingIndicator.style.display = 'none';

            console.error('Ошибка:', error);
            alert('Произошла ошибка при отправке файла на сервер.');
        });

    }

    // Проверяем наличие сохраненных данных в localStorage
    const savedData = localStorage.getItem('savedData');

    if (savedData) {
        // Если есть сохраненные данные, отображаем их при инициализации страницы
        const contentContainer = document.getElementById('content-container');
        contentContainer.innerHTML = savedData;
    }
});
