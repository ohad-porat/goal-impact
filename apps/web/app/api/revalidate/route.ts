import { revalidatePath } from 'next/cache'
import { NextRequest, NextResponse } from 'next/server'

const REVALIDATE_SECRET = process.env.REVALIDATE_SECRET

export async function POST(request: NextRequest) {
  const secret = request.headers.get('x-revalidate-secret')
  
  if (secret !== REVALIDATE_SECRET) {
    return NextResponse.json(
      { message: 'Invalid secret' }, 
      { status: 401 }
    )
  }

  try {
    const body = await request.json()
    const { paths } = body

    if (paths && Array.isArray(paths)) {
      paths.forEach((path: string) => {
        revalidatePath(path)
      })
    } else {
      revalidatePath('/')
      revalidatePath('/leagues')
      revalidatePath('/clubs')
      revalidatePath('/nations')
      revalidatePath('/players')
      revalidatePath('/leaders')
      revalidatePath('/leagues/[id]', 'page')
      revalidatePath('/clubs/[id]', 'page')
      revalidatePath('/nations/[id]', 'page')
      revalidatePath('/players/[id]', 'page')
      revalidatePath('/clubs/[id]/seasons', 'page')
      revalidatePath('/clubs/[id]/seasons/goals', 'page')
      revalidatePath('/players/[id]/goals', 'page')
    }

    return NextResponse.json({ 
      message: 'Revalidation successful',
      revalidated: true,
      timestamp: new Date().toISOString()
    })
  } catch (error) {
    return NextResponse.json(
      { message: 'Error revalidating', error: String(error) },
      { status: 500 }
    )
  }
}
