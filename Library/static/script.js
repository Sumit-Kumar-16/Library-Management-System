function toggleAdminCode() {
            var role = document.getElementById("roleSelect").value;
            var adminInput = document.getElementById("adminCodeInput");
            
            if (role === "librarian") {
                adminInput.style.display = "block";
                adminInput.required = true; 
            } else {
                adminInput.style.display = "none";
                adminInput.required = false;
            }
        }