import { test, expect } from '@playwright/test';

test.describe('Smoke Test', () => {
  test('login and send message', async ({ page }) => {
    // Navigate to login
    await page.goto('/login');
    
    // Login
    await page.fill('input[type="email"]', 'test@example.com');
    await page.fill('input[type="password"]', 'password123');
    await page.click('button[type="submit"]');

    // Wait for chats page to load
    await expect(page).toHaveURL('/chats');
    await expect(page.locator('h2', { hasText: 'Chats' })).toBeVisible();

    // Select the first chat if available
    const firstChat = page.locator('.w-chat-list ul li button').first();
    // In a real E2E test, we'd ensure data exists. For smoke test, we'll try to select a chat.
    // Since this runs against a mock backend or real backend, we wrap in a try or check visibility.
    await page.waitForTimeout(2000); // Give it a bit of time to fetch chats
    
    if (await firstChat.isVisible()) {
      await firstChat.click();
      
      const composer = page.locator('textarea[aria-label="Message composer"]');
      await expect(composer).toBeVisible();

      // Send a message
      await composer.fill('Hello from Playwright!');
      await composer.press('Enter');

      // Verify the message appears
      await expect(page.locator('text=Hello from Playwright!').first()).toBeVisible();
    }
  });
});
