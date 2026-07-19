import { Routes, Route, Navigate } from 'react-router-dom';
import { Landing } from '@/pages/Landing';
import { Login } from '@/pages/Login';
import { Register } from '@/pages/Register';
import { Jobs } from '@/pages/Jobs';
import { Applications } from '@/pages/Applications';
import { Profile } from '@/pages/Profile';
import { PostJob } from '@/pages/recruiter/PostJob';
import { ManagePosts } from '@/pages/recruiter/ManagePosts';
import { JobApplicants } from '@/pages/recruiter/JobApplicants';
import { ApplicantProfile } from '@/pages/recruiter/ApplicantProfile';
import { AdminUsers } from '@/pages/admin/AdminUsers';
import { AppLayout } from '@/layouts/AppLayout';
import { ProtectedRoute } from '@/components/ProtectedRoute';

function App() {
  return (
    <Routes>
      <Route path="/" element={<Landing />} />
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />

      {/* Job seeker */}
      <Route element={<ProtectedRoute allow={['user']} />}>
        <Route element={<AppLayout />}>
          <Route path="/dashboard" element={<Navigate to="/dashboard/jobs" replace />} />
          <Route path="/dashboard/jobs" element={<Jobs />} />
          <Route path="/dashboard/applications" element={<Applications />} />
        </Route>
      </Route>

      {/* Recruiter */}
      <Route element={<ProtectedRoute allow={['recruiter']} />}>
        <Route element={<AppLayout />}>
          <Route path="/recruiter" element={<Navigate to="/recruiter/posts" replace />} />
          <Route path="/recruiter/post" element={<PostJob />} />
          <Route path="/recruiter/posts" element={<ManagePosts />} />
          <Route path="/recruiter/posts/:jobId/applications" element={<JobApplicants />} />
          <Route path="/recruiter/applicants/:userId" element={<ApplicantProfile />} />
        </Route>
      </Route>

      {/* Admin */}
      <Route element={<ProtectedRoute allow={['admin']} />}>
        <Route element={<AppLayout />}>
          <Route path="/admin" element={<Navigate to="/admin/users" replace />} />
          <Route path="/admin/users" element={<AdminUsers />} />
        </Route>
      </Route>

      {/* Shared across any authenticated role */}
      <Route element={<ProtectedRoute />}>
        <Route element={<AppLayout />}>
          <Route path="/dashboard/profile" element={<Profile />} />
        </Route>
      </Route>

      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

export default App;
