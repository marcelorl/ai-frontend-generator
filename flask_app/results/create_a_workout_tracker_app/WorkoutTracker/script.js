const form = document.getElementById('myForm');
const exerciseInput = document.getElementById('exercise');
const setsInput = document.getElementById('sets');
const weightInput = document.getElementById('weight');
const addWorkoutButton = document.getElementById('addWorkoutButton');
const tableBody = document.getElementById('workout-table-body');

$(document).ready(function() {
  $('#myForm').validate({
    rules: {
      exercise: {
        required: true
      },
      sets: {
        nonNegativeInt: true
      },
      weight: {
        nonNegativeInt: true
      }
    }
  });
});

$(document).ready(function() {
  $('#myForm').submit(function(event) {
    if (!$('#myForm').valid()) {
      event.preventDefault();
    }
  });
});

addWorkoutButton.addEventListener('click', () => {
  const exercise = exerciseInput.value.trim();
  const sets = parseInt(setsInput.value.trim(), 10);
  const weight = parseInt(weightInput.value.trim(), 10);

  if (!exercise || !sets || !weight || sets < 0 || weight < 0) {
    alert('Please enter valid input values.');
    return;
  }

  const row = document.createElement('tr');
  row.innerHTML = `
    <td>${exercise}</td>
    <td>${sets}</td>
    <td>${weight}</td>
    <td><button class="btn btn-danger btn-sm delete">Delete</button></td>
  `;

  const deleteButton = row.querySelector('.delete');
  deleteButton.addEventListener('click', () => {
    row.remove();
  });

  tableBody.appendChild(row);

  exerciseInput.value = '';
  setsInput.value = '';
  weightInput.value = '';
});

// Custom validation method for non-negative integers
jQuery.validator.addMethod("nonNegativeInt", function(value, element) {
  return Number.isInteger(parseFloat(value)) && parseFloat(value) >= 0;
}, "Please enter a non-negative integer.");

// Edit feature
const editButtons = document.querySelectorAll('.edit');
editButtons.forEach(button => {
  button.addEventListener('click', () => {
    const index = parseInt(button.dataset.target, 10);
    const row = tableBody.children[index];
    exerciseInput.value = row.children[0].innerText;
    setsInput.value = row.children[1].innerText;
    weightInput.value = row.children[2].innerText;
    form.removeAttribute('data-index');
    addWorkoutButton.innerText = 'Update Workout';
  });
});