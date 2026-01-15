'use client';

import { useState, useEffect } from 'react';
import Image from 'next/image';
import Link from 'next/link';
import { getCart, updateCartItem, removeCartItem, createCheckoutSession, checkGiftCard } from '@/lib/api';
import type { Cart } from '@/types';

export default function CartPage() {
  const [cart, setCart] = useState<Cart | null>(null);
  const [loading, setLoading] = useState(true);
  const [updating, setUpdating] = useState<number | null>(null);
  const [checkingOut, setCheckingOut] = useState(false);

  // Gift card state
  const [giftCardCode, setGiftCardCode] = useState('');
  const [appliedGiftCard, setAppliedGiftCard] = useState<{ code: string; balance: number } | null>(null);
  const [giftCardError, setGiftCardError] = useState('');
  const [applyingGiftCard, setApplyingGiftCard] = useState(false);

  const fetchCart = async () => {
    try {
      const data = await getCart();
      setCart(data);
    } catch (error) {
      console.error('Failed to fetch cart:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCart();
  }, []);

  const handleUpdateQuantity = async (itemId: number, quantity: number) => {
    if (quantity < 1) return;
    setUpdating(itemId);
    try {
      await updateCartItem(itemId, quantity);
      await fetchCart();
    } catch (error) {
      console.error('Failed to update quantity:', error);
    } finally {
      setUpdating(null);
    }
  };

  const handleRemove = async (itemId: number) => {
    setUpdating(itemId);
    try {
      await removeCartItem(itemId);
      await fetchCart();
    } catch (error) {
      console.error('Failed to remove item:', error);
    } finally {
      setUpdating(null);
    }
  };

  const handleCheckout = async () => {
    setCheckingOut(true);
    try {
      const { checkout_url } = await createCheckoutSession(appliedGiftCard?.code);
      window.location.href = checkout_url;
    } catch (error) {
      console.error('Failed to create checkout session:', error);
      setCheckingOut(false);
    }
  };

  const handleApplyGiftCard = async () => {
    if (!giftCardCode.trim()) return;

    setApplyingGiftCard(true);
    setGiftCardError('');

    try {
      const result = await checkGiftCard(giftCardCode.trim());
      if (result.valid && result.balance) {
        setAppliedGiftCard({
          code: giftCardCode.trim().toUpperCase(),
          balance: parseFloat(result.balance),
        });
        setGiftCardCode('');
      } else {
        setGiftCardError(result.error || 'Invalid gift card');
      }
    } catch (error) {
      setGiftCardError('Gift card not found');
    } finally {
      setApplyingGiftCard(false);
    }
  };

  const handleRemoveGiftCard = () => {
    setAppliedGiftCard(null);
    setGiftCardError('');
  };

  // Calculate totals with gift card
  const subtotal = cart ? parseFloat(cart.subtotal) : 0;
  const giftCardDiscount = appliedGiftCard ? Math.min(appliedGiftCard.balance, subtotal) : 0;
  const estimatedTotal = subtotal - giftCardDiscount;

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="w-8 h-8 border-2 border-gray-300 border-t-gray-900 rounded-full animate-spin" />
      </div>
    );
  }

  if (!cart || cart.items.length === 0) {
    return (
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-16 text-center">
        <h1 className="text-3xl font-light tracking-wide mb-4">Your Cart</h1>
        <p className="text-gray-500 mb-8">Your cart is empty.</p>
        <Link
          href="/photos"
          className="inline-block px-8 py-3 bg-gray-900 text-white text-sm font-medium rounded hover:bg-gray-800 transition"
        >
          Continue Shopping
        </Link>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
      <h1 className="text-3xl font-light tracking-wide mb-8">Your Cart</h1>

      <div className="space-y-6">
        {cart.items.map((item) => {
          const itemLink = item.item_type === 'variant' && item.variant?.photo?.slug
            ? `/photos/${item.variant.photo.slug}`
            : item.product?.slug
              ? `/book/${item.product.slug}`
              : '#';

          return (
            <div
              key={item.id}
              className="flex gap-6 p-4 bg-gray-50 dark:bg-gray-800 rounded"
            >
              {/* Image */}
              <div className="relative w-24 h-24 bg-gray-200 dark:bg-gray-700 rounded overflow-hidden flex-shrink-0">
                {item.image ? (
                  <Image
                    src={item.image}
                    alt={item.title}
                    fill
                    className="object-cover"
                  />
                ) : (
                  <div className="w-full h-full flex items-center justify-center text-gray-400 text-xs">
                    No image
                  </div>
                )}
              </div>

              {/* Details */}
              <div className="flex-1 min-w-0">
                <Link
                  href={itemLink}
                  className="font-medium text-gray-900 dark:text-gray-100 hover:text-blue-600 dark:hover:text-blue-400 transition"
                >
                  {item.title}
                </Link>
                <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">{item.description}</p>

                <div className="flex items-center gap-4 mt-3">
                  <div className="flex items-center border border-gray-200 dark:border-gray-600 rounded">
                    <button
                      onClick={() => handleUpdateQuantity(item.id, item.quantity - 1)}
                      disabled={updating === item.id || item.quantity <= 1}
                      className="px-3 py-1 text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 disabled:opacity-50"
                    >
                      -
                    </button>
                    <span className="px-3 py-1 min-w-[40px] text-center text-gray-900 dark:text-gray-100">{item.quantity}</span>
                    <button
                      onClick={() => handleUpdateQuantity(item.id, item.quantity + 1)}
                      disabled={updating === item.id}
                      className="px-3 py-1 text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 disabled:opacity-50"
                    >
                      +
                    </button>
                  </div>

                  <button
                    onClick={() => handleRemove(item.id)}
                    disabled={updating === item.id}
                    className="text-sm text-red-600 dark:text-red-400 hover:text-red-700 dark:hover:text-red-300 disabled:opacity-50"
                  >
                    Remove
                  </button>
                </div>
              </div>

              {/* Price - self-center to vertically center with the row */}
              <div className="text-right flex-shrink-0 self-center">
                <p className="font-medium text-gray-900 dark:text-gray-100">${item.total_price}</p>
                {item.quantity > 1 && (
                  <p className="text-sm text-gray-500 dark:text-gray-400">${item.unit_price} each</p>
                )}
              </div>
            </div>
          );
        })}
      </div>

      {/* Summary */}
      <div className="mt-8 pt-8 border-t border-gray-200 dark:border-gray-700">
        {/* Gift Card Section */}
        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Gift Card
          </label>
          {appliedGiftCard ? (
            <div className="flex items-center justify-between p-3 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded">
              <div>
                <span className="font-medium text-green-800 dark:text-green-300">{appliedGiftCard.code}</span>
                <span className="text-sm text-green-600 dark:text-green-400 ml-2">
                  (${appliedGiftCard.balance.toFixed(2)} available)
                </span>
              </div>
              <button
                onClick={handleRemoveGiftCard}
                className="text-sm text-red-600 dark:text-red-400 hover:text-red-700"
              >
                Remove
              </button>
            </div>
          ) : (
            <div className="flex gap-2">
              <input
                type="text"
                value={giftCardCode}
                onChange={(e) => setGiftCardCode(e.target.value.toUpperCase())}
                placeholder="Enter gift card code"
                className="flex-1 px-3 py-2 border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 placeholder-gray-400"
              />
              <button
                onClick={handleApplyGiftCard}
                disabled={applyingGiftCard || !giftCardCode.trim()}
                className="px-4 py-2 bg-gray-200 dark:bg-gray-700 text-gray-800 dark:text-gray-200 rounded hover:bg-gray-300 dark:hover:bg-gray-600 transition disabled:opacity-50"
              >
                {applyingGiftCard ? '...' : 'Apply'}
              </button>
            </div>
          )}
          {giftCardError && (
            <p className="mt-2 text-sm text-red-600 dark:text-red-400">{giftCardError}</p>
          )}
        </div>

        {/* Totals */}
        <div className="space-y-2 mb-6">
          <div className="flex justify-between items-center">
            <span className="text-gray-600 dark:text-gray-400">Subtotal</span>
            <span className="text-gray-900 dark:text-gray-100">${subtotal.toFixed(2)}</span>
          </div>
          {appliedGiftCard && giftCardDiscount > 0 && (
            <div className="flex justify-between items-center text-green-600 dark:text-green-400">
              <span>Gift Card ({appliedGiftCard.code})</span>
              <span>-${giftCardDiscount.toFixed(2)}</span>
            </div>
          )}
          <div className="flex justify-between items-center pt-2 border-t border-gray-200 dark:border-gray-700">
            <span className="text-lg font-medium text-gray-900 dark:text-gray-100">Estimated Total</span>
            <span className="text-2xl font-medium text-gray-900 dark:text-gray-100">${estimatedTotal.toFixed(2)}</span>
          </div>
        </div>

        <p className="text-sm text-gray-500 dark:text-gray-400 mb-6">
          Shipping and taxes calculated at checkout.
        </p>

        <button
          onClick={handleCheckout}
          disabled={checkingOut}
          className="w-full py-4 bg-gray-900 dark:bg-gray-100 text-white dark:text-gray-900 font-medium rounded hover:bg-gray-800 dark:hover:bg-gray-200 transition disabled:opacity-50"
        >
          {checkingOut ? 'Redirecting to Checkout...' : 'Proceed to Checkout'}
        </button>

        <Link
          href="/photos"
          className="block text-center mt-4 text-sm text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200"
        >
          Continue Shopping
        </Link>
      </div>
    </div>
  );
}
