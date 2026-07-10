/*
 * =============================================================================
 * AI-First CRM HCP Module - App Component
 * =============================================================================
 * Author      : Ravi Kumar
 * Date        : 2026-07-09
 * Version     : 1.0.0
 * Description : Root application component with routing
 * Copyright (c) 2026. All rights reserved.
 * =============================================================================
 */

import { Routes, Route } from 'react-router-dom';

import Layout from '@/components/Layout';
import Dashboard from '@/pages/Dashboard';
import HCPManagement from '@/pages/HCPManagement';
import LogInteraction from '@/pages/LogInteraction';
import Interactions from '@/pages/Interactions';
import FollowUps from '@/pages/FollowUps';

function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route path="/" element={<Dashboard />} />
        <Route path="/hcps" element={<HCPManagement />} />
        <Route path="/log-interaction" element={<LogInteraction />} />
        <Route path="/interactions" element={<Interactions />} />
        <Route path="/follow-ups" element={<FollowUps />} />
      </Route>
    </Routes>
  );
}

export default App;