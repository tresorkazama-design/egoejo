import { http, HttpResponse } from 'msw';

const API_BASE = 'http://localhost:8000/api';

export const handlers = [
  // Intentions
  http.post(`${API_BASE}/intents/rejoindre/`, async ({ request }) => {
    const body = await request.json();
    return HttpResponse.json({ id: 1, ok: true, ...body }, { status: 200 });
  }),

  http.get(`${API_BASE}/intents/admin/`, ({ request }) => {
    const url = new URL(request.url);
    const page = url.searchParams.get('page') || '1';
    
    return HttpResponse.json({
      results: [
        { id: 1, nom: 'Test', email: 'test@example.com', profil: 'je-decouvre', date_creation: '2025-01-27' }
      ],
      total_pages: 1,
      current_page: parseInt(page)
    });
  }),

  http.delete(`${API_BASE}/intents/:id/delete/`, () => {
    return HttpResponse.json({ ok: true }, { status: 200 });
  }),

  http.get(`${API_BASE}/intents/export/`, () => {
    return HttpResponse.text('id,nom,email\n1,Test,test@example.com', {
      headers: { 'Content-Type': 'text/csv' }
    });
  }),

  // Projets
  http.get(`${API_BASE}/projets/`, () => {
    return HttpResponse.json({
      results: [
        { id: 1, titre: 'Projet 1', description: 'Description 1', montant_cible: 1000 },
        { id: 2, titre: 'Projet 2', description: 'Description 2', montant_cible: 2000 }
      ]
    });
  }),

  // Auth
  http.post(`${API_BASE}/auth/login/`, async ({ request }) => {
    const body = await request.json();
    if (body.username === 'test' && body.password === 'password') {
      return HttpResponse.json({
        access: 'test-access-token',
        refresh: 'test-refresh-token'
      });
    }
    return HttpResponse.json({ detail: 'Invalid credentials' }, { status: 401 });
  }),

  http.post(`${API_BASE}/auth/register/`, async ({ request }) => {
    const body = await request.json();
    return HttpResponse.json({ id: 1, ...body }, { status: 201 });
  }),

  http.get(`${API_BASE}/auth/me/`, ({ request }) => {
    const authHeader = request.headers.get('Authorization');
    // Accepter aussi les requêtes sans header pour les tests
    if (!authHeader || authHeader.startsWith('Bearer ')) {
      return HttpResponse.json({
        id: 1,
        username: 'testuser',
        email: 'test@example.com'
      });
    }
    return HttpResponse.json({ detail: 'Unauthorized' }, { status: 401 });
  }),

  // Handler pour les URLs de production (fallback)
  http.get('https://egoejo-production.up.railway.app/api/auth/me/', () => {
    return HttpResponse.json({
      id: 1,
      username: 'testuser',
      email: 'test@example.com'
    });
  }),

  // Chat
  http.get(`${API_BASE}/chat/messages/`, ({ request }) => {
    const url = new URL(request.url);
    const thread = url.searchParams.get('thread');
    return HttpResponse.json([]);
  }),

  http.post(`${API_BASE}/chat/messages/`, async ({ request }) => {
    const body = await request.json();
    return HttpResponse.json({
      id: Date.now(),
      ...body,
      author: { id: 1, username: 'testuser' },
      created_at: new Date().toISOString()
    }, { status: 201 });
  })
];

