from flask import Blueprint, render_template, flash, redirect, url_for, send_from_directory
from flask_login import login_required, current_user
from .forms import ShopItemsForm
from werkzeug.utils import secure_filename
from .models import Product
from . import db
import os



admin = Blueprint('admin', __name__)


@admin.route('/media/<path:filename>')
def get_image(filename):
    return send_from_directory('../media', filename)

@admin.route('/add-shop-items', methods=['GET', 'POST'])
@login_required
def add_shop_items():
    ADMIN_ID = 9 #create this variable, so in the future you can change only this variable.
    if current_user.id == ADMIN_ID:

        form = ShopItemsForm()
        if form.validate_on_submit():
            product_name = form.product_name.data
            current_price = form.current_price.data
            previous_price = form.previous_price.data
            in_stock = form.in_stock.data
            flash_sale = form.flash_sale.data
            product_picture = form.product_picture.data
            
            file = form.product_picture.data

            # if not os.path.exists('./media'):
            #     os.makedirs('./media')

            file_name = secure_filename(file.filename)
            file_path = f'./media/{file_name}' #REMOVE THIS LINE

            file.save(file_path)
            
            new_shop_item = Product()
            new_shop_item.product_name = product_name
            new_shop_item.current_price = current_price
            new_shop_item.previous_price = previous_price
            new_shop_item.in_stock = in_stock
            new_shop_item.flash_sale = flash_sale
            
            new_shop_item.product_picture = file_name
            
            try:
                db.session.add(new_shop_item)
                db.session.commit()
                flash(f'Product added successfully')
            except Exception as e:
                print(f"Error: {e}")
                flash('Error occurred while adding product')
                return "An error occurred", 500  # Handle the error properly
           

        return render_template('add_shop_items.html', form=form)

    return render_template('404.html') #activate this after testing

    
# =====================================================================================
ADMIN_ID = 9 #create this variable, so in the future you can change only this variable.
# =====================================================================================
@admin.route('/shop-items', methods=['GET', 'POST'])
@login_required
def shop_items():
    if current_user.id == ADMIN_ID:
        items = Product.query.order_by(Product.date_added).all()
        return render_template('shop_items.html', items=items)
    return render_template('404.html')

@admin.route('/update-item/<int:item_id>', methods=['GET', 'POST'])
@login_required
def update_item(item_id):
    if current_user.id == ADMIN_ID:
        form = ShopItemsForm()
        
        item_to_update = Product.query.get(item_id)
        
        form.product_name.render_kw = {'placeholder':item_to_update.product_name}
        form.previous_price.render_kw = {'placeholder':item_to_update.previous_price}
        form.current_price.render_kw = {'placeholder':item_to_update.current_price}
        form.in_stock.render_kw = {'placeholder':item_to_update.in_stock}
        form.flash_sale.render_kw = {'placeholder':item_to_update.flash_sale}
        
        if form.validate_on_submit():
            product_name = form.product_name.data
            current_price = form.current_price.data
            previous_price = form.previous_price.data
            in_stock = form.in_stock.data
            flash_sale = form.flash_sale.data
            
            file = form.product_picture.data
            file_name = secure_filename(file.filename)
            file_path = f'./media/{file_name}'
            file.save(file_path)
            
            try:
                Product.query.filter_by(id=item_id).update(dict(product_name=product_name,
                    current_price=current_price,
                    previous_price=previous_price,
                    in_stock=in_stock,
                    flash_sale=flash_sale,
                    product_picture=file_path))
                db.session.commit()
                flash(f'{product_name} Updated Successfully')
                print('Product Updated Successfully')
                return redirect('/shop-items')
            except Exception as e:
                print('product is not updated', e)
                flash(f'{product_name} is not updated')
            
        return render_template('update_item.html', form=form)
    return render_template('404.html')

@admin.route('/delete-item/<int:item_id>', methods=['GET', 'POST'])
def delete_item(item_id):
    # if current_user == 9:
        try:
            item_to_delete = Product.query.get(item_id)
            db.session.delete(item_to_delete)
            db.session.commit()
            flash(f'{item_to_delete.product_name} Deleted Successfully')
            print('Product Deleted Successfully')
            return redirect('/shop-items')
        except Exception as e:
            print('Item not deleted', e)
            flash('Item is not deleted')
            return redirect('/shop-items')
    # return render_template('404.html')