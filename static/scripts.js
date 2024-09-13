document.addEventListener("DOMContentLoaded", function() {
    const form = document.getElementById('checkin-form');
    
    form.addEventListener('submit', function(event) {
        event.preventDefault(); // Prevent default form submission behavior

        // Collect browser info
        const browser = navigator.userAgent;

        // Simple device detection based on user agent
        let device = "Unknown";
        if (/mobile/i.test(navigator.userAgent)) {
            device = "Mobile";
        } else if (/tablet/i.test(navigator.userAgent)) {
            device = "Tablet";
        } else {
            device = "Desktop";
        }

        // Prepare form data
        const formData = new FormData(form);
        formData.append('browser', browser);
        formData.append('device', device);

        // Debugging: Check if FormData is being created correctly
        for (let pair of formData.entries()) {
            console.log(`${pair[0]}: ${pair[1]}`);
        }

        // Send the form data
        fetch('/checkin', {
            method: 'POST',
            body: formData
        })
        .then(response => {
            if (response.redirected) {
                // If the response is a redirect, follow it
                window.location.href = response.url;
            } else {
                return response.text();
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
    });
});