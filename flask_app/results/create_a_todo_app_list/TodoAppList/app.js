document.addEventListener('DOMContentLoaded', () => {
  const form = document.querySelector('.todo-form');
  const todoInput = document.querySelector('#todo-input');
  const listGroup = document.querySelector('.list-group');

  // Add event listener to the form's submit event
  form.addEventListener('submit', (e) => {
    e.preventDefault();

    // Create a new list item with the text from the input field
    const newListItem = document.createElement('li');
    newListItem.classList.add('list-group-item', 'd-flex', 'justify-content-between', 'align-items-center');
    newListItem.textContent = todoInput.value;

    // Add a remove button for the list item
    const removeBtn = document.createElement('button');
    removeBtn.classList.add('btn', 'btn-danger', 'ms-2');
    removeBtn.textContent = 'Remove';

    // Implement event listener for the remove button
    removeBtn.addEventListener('click', () => {
      newListItem.remove();
    });

    // Add the remove button to the list item
    newListItem.appendChild(removeBtn);

    // Add the new list item to the list group
    listGroup.appendChild(newListItem);

    // Clear the input field
    todoInput.value = '';
  });
});