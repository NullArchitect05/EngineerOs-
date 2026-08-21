import { Loader2 } from 'lucide-react';

export default function LoadingSkeleton() {
  return (
    <div className='space-y-6 animate-pulse'>
      <div className='grid grid-cols-1 md:grid-cols-4 gap-6'>
        {[...Array(4)].map((_, i) => (
          <div key={i} className='p-6 md:p-8 rounded-2xl bg-slate-900/40 border border-slate-800/50'>
            <div className='w-20 h-20 rounded-full bg-slate-800 mx-auto mb-4' />
            <div className='h-4 bg-slate-800 rounded w-24 mx-auto' />
          </div>
        ))}
      </div>
      <div className='p-6 md:p-8 rounded-2xl bg-slate-900/40 border border-slate-800/50'>
        <div className='h-4 bg-slate-800 rounded w-32 mb-6' />
        <div className='space-y-3'>
          {[...Array(5)].map((_, i) => (
            <div key={i} className='flex items-center gap-3'>
              <div className='w-2 h-2 rounded-full bg-slate-800' />
              <div className='h-3 bg-slate-800 rounded flex-1' />
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
