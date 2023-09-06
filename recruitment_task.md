# Tylko Ecommerce Team - Interview Task

## Background
The aim of this coding exercise is to implement a simplified shopping flow API. Adding to cart and making an order. 
The main requirement is to allow certain daily ordering limits - per region and global for the whole shop.

## Technical requirements
Django + DRF

## Exercise process
Create an empty, private, Github repository and add the following 4 users as collaborators:
- AgnieszkaPlatek
- kermox
- KJagiela
- natancamenzind
Leave the master empty. Commit your code to a fresh new branch and create a Pull Request
to the master. Do not forget to add all 4 users as Reviewers on the PR.

## Business Requirements
Limits are per day! There are 2 kinds of limits:
1. Regional limit (ie. UK/DE/FR/PL/NL) - It’s either 0, some number, or unlimited
2. Global limit - It’s always greater than 0

Both limits need to allow for Order to be accepted. So if the Regional limit allows an order but Global does not - the order is rejected. 
The same thing happens when the Region limit does not allow it but Global does - the order is rejected.

Additionally, have in mind that:
- Limits are counted against Orders, not Carts.
- Customers must be able to buy multiple products as long as limits allow for them.
- Customers can make multiple orders from multiple regions.
- Implement some kind of cart and order status fields.
- User management is not the focus of this exercise so any kind is acceptable

## Minimal suggested Models
Shelf, Cart, Order


## Minimal endpoints requirements
1. /api/add_to_cart
	Input: shelf_id, region
	Output: cart_id, cart_status, shelves in cart
2. /api/make_order
	Input: cart_id, region
	Output: order_id, order_status, shelves in order
	Remember about regional and global daily limits

## Evaluation criteria
There are certain aspects that will be considered when evaluating your solution:
- code quality (especially readability and ease of maintenance)
- expertise in using the framework
- ease of modification (imagine we need to change the limits to be counted weekly - at some point in the future)

**Unit Tests are highly desirable**

## Tips
In case you are not sure about something - use your best judgment. The aim of this exercise is for you to show us how you think and approach problems. Try to imagine you are implementing this system for a real-world shop - your own.