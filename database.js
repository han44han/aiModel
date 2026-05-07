import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'

const SUPABASE_URL = 'https://dceuyznzgcaluvzzexxh.supabase.co'
const SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRjZXV5em56Z2NhbHV2enpleHhoIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzY4Nzg5MzcsImV4cCI6MjA5MjQ1NDkzN30.QAUrzaoqLV19qw2XmhEwRg9ZuAIb6KQzqr0IHh2dVI4'

export const supabase = createClient(SUPABASE_URL, SUPABASE_KEY)