import { createBrowserRouter } from 'react-router-dom';
import { lazy, Suspense } from 'react';
import Layout from '../components/Layout';
import { Loader } from '../components/Loader';
import ErrorBoundary from '../components/ErrorBoundary';
import PageViewTracker from '../components/PageViewTracker';

// Lazy loading des pages pour améliorer les performances
const Home = lazy(() => import('./pages/Home'));
const Univers = lazy(() => import('./pages/Univers'));
const Vision = lazy(() => import('./pages/Vision'));
const Citations = lazy(() => import('./pages/Citations'));
const Alliances = lazy(() => import('./pages/Alliances'));
const Projets = lazy(() => import('./pages/Projets'));
const Contenus = lazy(() => import('./pages/Contenus'));
const Communaute = lazy(() => import('./pages/Communaute'));
const Votes = lazy(() => import('./pages/Votes'));
const Rejoindre = lazy(() => import('./pages/Rejoindre'));
const Chat = lazy(() => import('./pages/Chat'));
const Login = lazy(() => import('./pages/Login'));
const Register = lazy(() => import('./pages/Register'));
const Admin = lazy(() => import('./pages/Admin'));
const Impact = lazy(() => import('./pages/Impact'));
const Dashboard = lazy(() => import('./pages/Dashboard'));
const MyCard = lazy(() => import('./pages/MyCard'));
const RacinesPhilosophie = lazy(() => import('./pages/RacinesPhilosophie'));
const Mycelium = lazy(() => import('./pages/Mycelium'));
const Podcast = lazy(() => import('./pages/Podcast'));
const SakaSilo = lazy(() => import('./pages/SakaSilo')); // Phase 3 SAKA : Compostage & Silo Commun
const SakaMonitor = lazy(() => import('./pages/SakaMonitor')); // SAKA Monitoring & KPIs (Admin)
const SakaSeasons = lazy(() => import('./pages/SakaSeasons')); // Saisons SAKA (Cycles)
const NotFound = lazy(() => import('./pages/NotFound'));

// Composant wrapper pour le lazy loading
// Le fallback est minimal pour éviter les flashs visuels
const LazyPage = ({ children }) => (
  <ErrorBoundary>
    <Suspense fallback={<div style={{ minHeight: '100vh', background: 'transparent', backgroundColor: 'transparent', width: '100%', height: '100%' }} />}>
      {children}
    </Suspense>
  </ErrorBoundary>
);

export const appRouter = createBrowserRouter([
  {
    path: '/',
    element: (
      <>
        <PageViewTracker />
        <Layout />
      </>
    ),
    children: [
      {
        index: true,
        element: <LazyPage><Home /></LazyPage>
      },
      {
        path: 'univers',
        element: <LazyPage><Univers /></LazyPage>
      },
      {
        path: 'vision',
        element: <LazyPage><Vision /></LazyPage>
      },
      {
        path: 'citations',
        element: <LazyPage><Citations /></LazyPage>
      },
      {
        path: 'alliances',
        element: <LazyPage><Alliances /></LazyPage>
      },
      {
        path: 'projets',
        element: <LazyPage><Projets /></LazyPage>
      },
      {
        path: 'contenus',
        element: <LazyPage><Contenus /></LazyPage>
      },
      {
        path: 'communaute',
        element: <LazyPage><Communaute /></LazyPage>
      },
      {
        path: 'votes',
        element: <LazyPage><Votes /></LazyPage>
      },
      {
        path: 'rejoindre',
        element: <LazyPage><Rejoindre /></LazyPage>
      },
      {
        path: 'chat',
        element: <LazyPage><Chat /></LazyPage>
      },
      {
        path: 'login',
        element: <LazyPage><Login /></LazyPage>
      },
      {
        path: 'register',
        element: <LazyPage><Register /></LazyPage>
      },
      {
        path: 'admin',
        element: <LazyPage><Admin /></LazyPage>
      },
      {
        path: 'impact',
        element: <LazyPage><Impact /></LazyPage>
      },
      {
        path: 'dashboard',
        element: <LazyPage><Dashboard /></LazyPage>
      },
      {
        path: 'my-card',
        element: <LazyPage><MyCard /></LazyPage>
      },
      {
        path: 'racines-philosophie',
        element: <LazyPage><RacinesPhilosophie /></LazyPage>
      },
      {
        path: 'mycelium',
        element: <LazyPage><Mycelium /></LazyPage>
      },
      {
        path: 'podcast',
        element: <LazyPage><Podcast /></LazyPage>
      },
      {
        path: 'saka/silo',
        element: <LazyPage><SakaSilo /></LazyPage>
      },
      {
        path: 'saka/saisons',
        element: <LazyPage><SakaSeasons /></LazyPage>
      },
      {
        path: 'admin/saka-monitor',
        element: <LazyPage><SakaMonitor /></LazyPage>
      },
      {
        path: '*',
        element: <LazyPage><NotFound /></LazyPage>
      }
    ]
  }
]);

